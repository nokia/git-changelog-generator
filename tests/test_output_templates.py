#!/usr/bin/env python2

"""Unit test suite for functions related to version handling"""

from argparse import Namespace
import gcg.jinja_filters


def test_commit_headline_ok():
    """
    basic success scenario of commit_headline filter
    """
    fake_commit = Namespace(message="""This is a   \

    multi-line message with spaces at the   end   \

    of some lines      \

    """)
    assert gcg.jinja_filters.commit_headline(fake_commit) == "This is a"
