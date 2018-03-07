#!/usr/bin/env python2

"""
Unit and component tests for the main module
"""

from __future__ import print_function
import os
import shutil
import tempfile

import gcg
import gcg.entrypoint
import gcg.errors as err
from tests.helpers.gitrepo import prepare_git_repo, AUTHOR


class TestMain(object):
    """Unit test suite for main functionality. May be split into
    smaller parts with time."""

    # pylint: disable=unused-argument,missing-docstring
    # pylint: disable=attribute-defined-outside-init,duplicate-code
    def setup_method(self, test_method):
        self.tmp_dir = tempfile.mkdtemp()

    # pylint: disable=unused-argument,missing-docstring
    def teardown_method(self, test_method):
        shutil.rmtree(self.tmp_dir)

    @staticmethod
    def test_main_rpm():
        """Generate changelog for THIS repo. Illustrative purposes only"""
        test_path = os.path.dirname(os.path.abspath(__file__))
        repo_path = os.path.join(test_path, '..')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', repo_path, '-O', 'rpm'])

    @staticmethod
    def test_main_deb():
        """Generate changelog for THIS repo. Illustrative purposes only"""
        test_path = os.path.dirname(os.path.abspath(__file__))
        repo_path = os.path.join(test_path, '..')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', repo_path, '-O', 'deb', '-n', 'FOOBAR',
            '--deb-distribution', 'xenial'])

    def test_main_rpm_fakerepo(self):
        """
        Generate a changelog from a well known and defined repository
        which we control ourselves.
        """

        input_messages = [
            "Initial commit",
            "And then a second commit",
            "ISSUE-1 And a third commit\nThis time with a Jira ticket",
        ]

        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)
        assert not repo.bare
        assert not client.tag()

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'rpm', '-o', out_file])
        assert os.path.exists(out_file)

        lines = [line.rstrip('\n') for line in open(out_file)]
        assert lines[0].endswith(
            '{} <{}> - current'.format(AUTHOR.name, AUTHOR.email))
        assert lines[1].startswith('- ISSUE-1 And a third commit')
        assert lines[2].startswith('- And then a second commit')
        assert lines[3].startswith('- Initial commit')

    def test_main_deb_fakerepo(self):
        """
        Generate a changelog from a well known and defined repository
        which we control ourselves - DEB
        """
        input_messages = [
            "First",
            "Second",
        ]

        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)
        assert not repo.bare
        assert client

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'deb', '-o', out_file, '-n', 'foopkg',
            '-D', 'xenial'])
        assert os.path.exists(out_file)

        lines = [line.rstrip('\n') for line in open(out_file)]
        lines = filter(len, lines)
        assert lines[0] == 'foopkg (current) xenial; urgency=low'
        assert lines[1].startswith('  * Second')
        assert lines[2].startswith('  * First')

    def test_main_deb_custom_urgency(self):
        """
        Verify the deb urgency is recorded as appropriate
        """
        input_messages = [
            "First",
        ]

        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)
        assert not repo.bare
        assert client

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'deb', '-o', out_file, '-n', 'package',
            '-D', 'xenial', '-U', 'high'])
        assert os.path.exists(out_file)

        lines = [line.rstrip('\n') for line in open(out_file)]
        lines = filter(len, lines)
        assert lines[0] == 'package (current) xenial; urgency=high'
        assert lines[1].startswith('  * First')

    def test_main_only_jira_issues(self):
        """
        Validate that with -b option, only commits containing
        JIRA issues (default) are included
        """

        input_messages = [
            "Initial commit",
            "And then a second commit",
            "ISSUE-1 And a third commit\nThis time with a Jira ticket",
        ]

        # pylint: disable=unused-variable
        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'rpm', '-o', out_file, '-b'])
        assert os.path.exists(out_file)

        lines = [line.rstrip('\n') for line in open(out_file)]
        assert len(lines) == 3
        assert lines[0].endswith('> - current')
        assert lines[1].startswith('- ISSUE-1 And a third commit')

    def test_only_gitlab_issues(self):
        """
        Validate that with -b option, only commits containing
        gitlab issues by passing in a -B and a custom pattern
        """

        input_messages = [
            "Initial commit",
            "Issue #312 Resolve the bug",
        ]

        # pylint: disable=unused-variable
        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'rpm', '-o', out_file, '-b',
            '-B', r'Issue #\d+\b'])

        lines = [line.rstrip('\n') for line in open(out_file)]
        assert len(lines) == 3
        assert lines[0].endswith('> - current')
        assert lines[1].startswith('- Issue #312 Resolve the bug')

    def test_merge_repo(self):
        input_messages = ["1", "2", "3"]

        (path, repo, client) = prepare_git_repo(
            self.tmp_dir, messages=input_messages)
        test_branch = repo.create_head('test_branch', 'HEAD~1')

        repo.head.reference = test_branch
        repo.index.commit('4')
        repo.head.reference = repo.heads.master
        repo.index.commit('5')
        client.merge('--no-ff', '-m 6', 'test_branch')

        out_file = os.path.join(self.tmp_dir, 'outfile')
        assert err.SUCCESS == gcg.entrypoint.main([
            'xyz', '-p', path, '-O', 'rpm', '-o', out_file])
        assert os.path.exists(out_file)

        lines = [line.rstrip('\n') for line in open(out_file)]
        lines = filter(len, lines)
        print(lines)

        count = len(lines)
        for i in range(1, count):
            assert lines[count-i].startswith('- {}'.format(i))
