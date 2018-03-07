#!/usr/bin/env python2.7
# encoding: utf-8

'''
UT Helper functions related to Git repository setup.
'''
import os

import git


AUTHOR = git.Actor("Pytest Forever", "author@example.com")


def prepare_git_repo(root, dirname='testrepo', messages=None):
    """Create a Git repository at a given path
    and optionally pre-populate it with commits

    :param root: root directory
    :param dirname: repository directory (within root). This directory
                    will be automatically created.
    :param messages: a list of strings which will be used for commit messages

    """
    if messages is None:
        messages = []
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

    return (path, repo, client)
