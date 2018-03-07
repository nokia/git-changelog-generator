#!/usr/bin/env python2

"""
gcg stands for Git Changelog Generator
This module can be used to traverse the Git version tree
between specified commits (by default, from HEAD to the first reachable
commit) and produce a DEB or RPM changelog output, treating
tags as release points.

Note that only tags conforming to semver.org policies are treated
as releases.

"""
from __future__ import print_function

import argparse
import collections
import email.utils
import logging
import os
import re
import sys
import time

import git
import jinja2
import jinja2.environment

import gcg.errors as err
from gcg.tag_filter import TagFilter
from gcg.jinja_filters import commit_headline


def parse_args(argv):
    """Parse user's command-line parameters

    :param argv: User arguments
    :returns: object with configuration (as provided by argparse)
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate changelogs out of Git history.",
        epilog="""
        FIXME: timezone manipulations
        FIXME: potential time conflicts (merging in old changes
        to a new release).
        TODO: better test coverage
        """
    )
    parser.add_argument(
        '-p', '--path',
        help="""Git repository path""",
        type=str, action="store",
        default=os.getcwd(),
    )
    parser.add_argument(
        '-O', '--output-format',
        help="""Output changelog format""",
        type=str, action="store", choices=['rpm', 'deb'],
        required=True
    )
    parser.add_argument(
        '-o', '--output-file',
        help="""Output file path. Uses standard output when omitted""",
        type=str, action="store",
    )
    parser.add_argument(
        '-u', '--until',
        help="Most recent (top) commit to include in the "
             "changelog. This is the commit from which history discovery"
             "begins",
        type=str, action="store",
        default='HEAD'
    )
    parser.add_argument(
        '-s', '--since',
        help="Oldest commit to include in the changelog",
        type=str, action="store"
    )
    parser.add_argument(
        '-c', '--current-version',
        help="""Version to be assigned to the revisions between
        the last tagged version and specified <end-commit> (e.g. HEAD).
        For example: .... (FIXME)""",
        type=str, action="store",
        default='current'
    )
    parser.add_argument(
        '-x', '--exclude-merges',
        help="Filter out the merge commits out of changelog.",
        action="store_true",
    )
    parser.add_argument(
        '-b', '--bug-tracking-only',
        help="Process only commits which have a bug tracking"
             "issue reference in the message (e.g. a Jira ticket).",
        action="store_true",
    )
    parser.add_argument(
        '-B', '--bug-tracking-pattern',
        help="Provide the pattern (Python regexp) to check against commit"
             "messages when using --bug-tracking-only option."
             "The default value matches a standard Jira issue reference.",
        action="store", default=r'\b(([A-Z]{1,10})-?)[A-Z]+-[1-9]+\d*\b'
    )
    parser.add_argument(
        '-t', '--prefer-tags',
        help="""Retrieve the release information (date and release author)
        from tags. When false (the default), the information will
        be extracted from the most recent commit preceding the tag
        or commit specified by --until option.""",
        action="store_true",
    )
    parser.add_argument(
        '-T', '--custom-tag-pattern',
        help="""Provide the pattern (Python regexp) to match against Git tags.
        Tags which don't match the pattern will not be considered as releases.
        When omitted, tag names will be validated against Semantic
        Versioning (semver.org) rules.""",
        action="store"
    )
    parser.add_argument(
        '-D', '--deb-distribution',
        help="""Distribution for the deb package.
        NOTE: mandatory when the output format (-O) is 'deb'.""",
        action="store"
    )
    parser.add_argument(
        '-n', '--deb-package-name',
        help="""Package name (in case it's a Debian package).
        NOTE: mandatory when the output format (-O) is 'deb'.""",
        action="store",
    )
    parser.add_argument(
        '-U', '--deb-urgency',
        help="""Default urgency value for Debian releases.
        NOTE: this is a single value which will be populated across
        the whole changelog, for all releases.""",
        action="store", default='low',
        choices=['low', 'medium', 'high', 'emergency', 'critical']
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Verbosity level. Specify twice for debug logs as well.",
        action="count", default=0
    )

    options = parser.parse_args(argv)
    if options.output_format == 'deb':
        if options.deb_package_name is None:
            raise ValueError("For 'deb', the package name (-n) is mandatory")
        if options.deb_distribution is None:
            raise ValueError("For 'deb', the --deb-distribution is mandatory")

    return options


def get_commit_tags(client, commit):
    """
    Retrieve tags pointing at a specific commit/revision
    :param client: an initialized git.Git() object to query with
    :param commit:
    :return: list of strings containing tags pointing at specified
             revision; may be empty if there's no tag at this revision
    """
    retval = []
    (status, output, errors) = client.tag(
        '--points-at', commit.hexsha, with_extended_output=True)
    if status:
        logging.error(errors)
    else:
        if output:
            retval = output.split('\n')
    return retval


def collate_entry_header_data(repo, entries, options):
    """
    :param repo:
    :param entries: an OrderedDict object with keys being tag names (string)
                    and values being a list of git.Commit objects
    :param options: user input parameters
    :return: dictionary; k: tag name, v: object with properties
                datetime
    """
    retval = {}
    for version in entries:
        if not version or (entries[version] and not options.prefer_tags):
            hdr = log_entry_header_from_commit(entries[version][0])
        else:
            logging.info("Retrieving details of tag '%s'", version)
            hdr = log_entry_header_from_tag(repo.tags[version].tag)
        hdr['version'] = version or options.current_version
        hdr['deb_urgency'] = options.deb_urgency
        hdr['deb_distro'] = options.deb_distribution
        hdr['deb_name'] = options.deb_package_name
        retval[version] = hdr
    return retval


def log_entry_header_from_commit(the_commit):
    """
    Retrieve information for the release line from the commit
    :param the_commit: a git.Commit object
    :return: dictionary
    """
    # FIXME: how about timezones, dear people?
    hdr = dict()
    hdr['date'] = time.gmtime(the_commit.authored_date)
    hdr['date_rpm'] = time.strftime('%a %b %d %Y', hdr['date'])
    hdr['date_deb'] = email.utils.formatdate(the_commit.authored_date)
    hdr['author'] = str(the_commit.author.name)
    hdr['email'] = str(the_commit.author.email)
    return hdr


def log_entry_header_from_tag(tag):
    """
    Retrieve information for the release line from the tag
    :param tag: a git.Tag object
    :return: dictionary
    """
    # FIXME: how about timezones, dear people?
    hdr = dict()
    authored_date = tag.tagged_date
    hdr['date'] = time.gmtime(authored_date)
    hdr['date_rpm'] = time.strftime('%a %b %d %Y', hdr['date'])
    hdr['date_deb'] = email.utils.formatdate(authored_date)
    hdr['author'] = str(tag.tagger.name)
    hdr['email'] = str(tag.tagger.email)
    return hdr


def log_level_from_verbosity(count):
    """Convert verbosity (-v) count into an appropriate
    log level
    :param count: integer; number of -v flags used
    :returns: a log level value
    """
    retval = logging.WARNING
    if count == 1:
        retval = logging.INFO
    elif count == 2:
        retval = logging.DEBUG
    return retval


def init_jinja_env(external_template_dir=None):
    """
    Initialize Jinja environment:
    - load templates embedded in the gcg module
    - optionally load from an external template directory
    - register custom Jinja filters
    :param external_template_dir: optional; when provided, templates from given
                                  directory will be looked up first
    :return: the newly created Jinja environment
    """
    loaders = []
    if external_template_dir:
        loaders.append(jinja2.FileSystemLoader(external_template_dir))
    loaders.append(jinja2.PackageLoader('gcg'))

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader(loaders)
    )
    env.filters['commit_headline'] = commit_headline
    return env


# pylint: disable=too-many-return-statements
def main(argv=None):
    """
    Main entry point
    :param argv: optional script parameters; default is to use sys.argv
    :return:
    """
    if argv is None:
        argv = sys.argv

    try:
        options = parse_args(argv[1:])
    except ValueError as exc:
        print("Invalid input; details: {}".format(exc), file=sys.stderr)
        return err.INVALID_INPUT

    loglevel = log_level_from_verbosity(options.verbose)
    logging.basicConfig(
        level=loglevel, format="[%(levelname)s] %(message)s")

    try:
        repo = git.Repo(options.path)
    except ValueError as exc:
        logging.error("Invalid input; details: %s", exc)
        return err.INVALID_INPUT
    except git.NoSuchPathError as exc:
        logging.error("Path specified with '-p' does not exist; %s", exc)
        return err.REPO_PATH_INVALID
    except git.InvalidGitRepositoryError as exc:
        logging.error("Path specified with '-p' does not a Git repo make; %s",
                      exc)
        return err.REPO_PATH_NOT_REPO

    try:
        client = git.Git(options.path)
        upper_limit = resolve_commit_from_arguments(repo, options, 'until')
        lower_limit = resolve_commit_from_arguments(repo, options, 'since')
    except ValueError as exc:
        logging.error("Invalid input values for changelog scope; details: "
                      "%s.", exc)
        return err.INVALID_VCS_LIMITS

    try:
        entries = traverse_version_tree(
            client, repo, options, upper_limit, lower_limit)
        headers = collate_entry_header_data(repo, entries, options)

    except ValueError as exc:
        logging.error("Program aborted; details: %s.", exc)
        return err.PROCESSING_FAILED

    print_changelog(entries, headers, options.output_format,
                    options.output_file)

    return err.SUCCESS


def print_changelog(entries, headers, output_format, output_file=None):
    """
    Render the changelog report
    :param entries: typically commit objects
    :param headers: release headers (dictionary with release tag as key)
    :param output_format: string, e.g. 'rpm' or 'deb'
    :param output_file: optional; file name to write to. By default write
                        to standard output
    :return: n/a
    """
    environment = init_jinja_env()
    template = environment.get_template(output_format)
    output = template.render(entries=entries, headers=headers)
    if output_file:
        with open(output_file, 'w') as ofile:
            ofile.write(output)
    else:
        print(output)


def commit_filtered_out(commit, options, bugtracking_regex):
    """
    Decide if commit should be processed or not

    :param commit: Commit to be inspected
    :param options: command-line options
    :param bugtracking_regex: regular expression object to match
                              against the commit message. Only used if
                              options.bug_tracking_only evaluates to True
    :return: True / False
    """
    retval = False
    if options.exclude_merges and len(commit.parents) > 1:
        logging.info("Ignoring merge commit %s", commit)
        retval = True
    elif options.bug_tracking_only:
        if not bugtracking_regex.match(commit.message):
            logging.info("Ignoring commit %s (no bug reference)", commit)
            retval = True
    return retval


def repo_iterate(repo, high, low=None):
    """
    Return (yield) one commit by one, from 'high' to 'low'
    (or oldest reachable commit) and in reverse chronological order
    (see rev-list and git log commands)

    :param repo: an initialized git.Repo object
    :param high: top of the version tree to scan; typically tip of the branch,
                HEAD, but it can be any commit
    :param low: optional; the low end of the revision list. When unspecified,
                function will scan the history until the first reachable commit
    :return: a git.Commit object
    """

    refs = high if low is None else "{}..{}".format(high, low)

    for commit in repo.iter_commits(refs):
        yield commit


def traverse_version_tree(client, repo, options, upper_limit, lower_limit):
    """
    Scan the version tree and return the entries
    :param client: an initialized git.Git() object to query with
    :param repo: reference to the repository (git.Repo())
    :param options: command-line options as specified by the user
    :param upper_limit: the top commit from which scanning begins
    :param lower_limit: the bottom commit where scanning the version
                        tree ends; if None, scan will continue until
                        the very first reachable commit
    :return: an OrderedDict object with keys being tag names (string)
             and values being a list of git.Commit objects
    """
    entries = collections.OrderedDict()
    curr_entry = list()
    curr_tag = ''
    bugtracking_regexp = re.compile(options.bug_tracking_pattern, re.MULTILINE)
    tag_filter = TagFilter(None)

    for commit in repo_iterate(repo, upper_limit, lower_limit):
        logging.debug("Processing commit %s (%s)", commit.hexsha,
                      commit_headline(commit))
        tags = tag_filter.matching_only(get_commit_tags(client, commit))
        if tags:
            if curr_entry:
                entries[curr_tag] = curr_entry
            # TODO: handle more tags pointing to the same commit (somehow)
            curr_tag = tags[0]
            curr_entry = list()

        if not commit_filtered_out(commit, options, bugtracking_regexp):
            curr_entry.append(commit)
    if curr_entry:
        entries[curr_tag] = curr_entry
    return entries


def resolve_commit_from_arguments(repo, options, arg_name):
    """
    Resolve a reference to a commit (by branch name, label or sha)
    to an actual commit id
    :param arg_name: name of the command-line argument to resolve
    :param options: command-line options
    :param repo: reference to a repository (initialized)
    :returns: a commit id as string
    :raises: ValueError when the reference cannot be found within the repo
    """
    retval = None
    ref = getattr(options, arg_name)
    if ref is not None:
        invalid_commit_msg = "Value of argument --%s does not not resolve " \
                             "to a valid commit in this repository"
        try:
            retval = repo.commit(ref)
            logging.info("Commit referred to as '%s' (%s) resolved to %s",
                         arg_name, ref, retval.hexsha)
        except git.BadName as exc:
            logging.error(invalid_commit_msg, arg_name)
            raise ValueError(exc)
        except ValueError:
            logging.error(invalid_commit_msg, arg_name)
            raise
    return retval
