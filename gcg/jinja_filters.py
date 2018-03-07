#!/usr/bin/env python2

"""
Collection of filter functions which can be used in Jinja2 templates
"""


# pylint: disable=unused-argument
def commit_headline(commit, unused=None):
    """
    A helper function to retrieve the headline from a git.Commit message
    :param commit: a git.Commit object
    :param unused: n/a (Jinja passes it anyway)
    :return: a headline of the commit - first, stripped line of the message
    """
    return commit.message.split('\n', 1)[0].strip()
