#!/usr/bin/env python2.7
# encoding: utf-8

'''
UT Helper functions related to Git repository setup.
'''
import os

import git


AUTHOR = git.Actor("Pytest Forever", "author@example.com")


def change_author_email(repo, email):
    """Change author email. The git config must already be initialized.
    :param repo: The repository to use.
    :param email: The new email address.
    """
    if email is not None:
        writer = repo.config_writer(config_level='repository')
        writer.set('user', 'email', email)
        writer.release()


def prepare_git_repo(root, dirname='testrepo', messages=None,
                     messages_and_tags=None):
    """Create a Git repository at a given path
    and optionally pre-populate it with commits

    :param root: root directory
    :param dirname: repository directory (within root). This directory
                    will be automatically created.
    :param messages: a list of strings which will be used for commit messages.
    :param messages_and_tag: a list of tuples which will be used for commit
                             messages and corresponding tags.
                             If the tuple has 2 elements, then a lightweight
                             tag is created. If the tuple has 3 elements,
                             then an annotated tag is created. If the tuple
                             has 4 elements, the fourth element is used as
                             mail-address of the tag-committer.
    """
    if messages is None:
        messages = []
    if messages_and_tags is None:
        messages_and_tags = []
    # This is so that CI environment doesn't override it
    os.environ['GIT_AUTHOR_NAME'] = AUTHOR.name
    os.environ['GIT_AUTHOR_EMAIL'] = AUTHOR.email
    path = os.path.join(root, dirname)
    repo = git.Repo.init(path, bare=False)
    index = repo.index
    client = git.Git(path)
    writer = repo.config_writer(config_level='repository')
    writer.add_section('user')
    writer.set('user', 'name', AUTHOR.name)
    writer.set('user', 'email', AUTHOR.email)
    writer.release()

    # commit by commit message and author and committer
    for msg in messages:
        index.commit(msg)
    for msg_with_tag in messages_and_tags:
        commit = index.commit(msg_with_tag[0])
        if msg_with_tag[1] is not None:
            if len(msg_with_tag) > 3:
                change_author_email(repo, msg_with_tag[3])
                repo.create_tag(msg_with_tag[1], commit, msg_with_tag[2])
                change_author_email(repo, AUTHOR.email)
            elif len(msg_with_tag) > 2:
                repo.create_tag(msg_with_tag[1], commit, msg_with_tag[2])
            else:
                repo.create_tag(msg_with_tag[1], commit)

    return (path, repo, client)
