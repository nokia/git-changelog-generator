#!/usr/bin/env python2.7
# encoding: utf-8

'''
Test cases for simple functions which don't fit anywhere else (as of yet).
'''
import argparse
import collections
import logging
import shutil

import os
import tempfile

import gcg


class TestHelperFunctions(object):
    """Tests of remaining helper functions"""

    # pylint: disable=unused-argument,missing-docstring
    # pylint: disable=attribute-defined-outside-init
    def setup_method(self, test_method):
        self.temp_dir = tempfile.mkdtemp()

    # pylint: disable=unused-argument,missing-docstring
    def teardown_method(self, test_method):
        shutil.rmtree(self.temp_dir)

    @staticmethod
    def test_loglevels_mapping():
        from gcg.entrypoint import log_level_from_verbosity

        assert logging.WARNING == log_level_from_verbosity(0)
        assert logging.WARNING == log_level_from_verbosity(-1)
        assert logging.WARNING == log_level_from_verbosity(3)

        assert logging.INFO == log_level_from_verbosity(1)
        assert logging.DEBUG == log_level_from_verbosity(2)

    def test_print_changelog_file_ok(self):
        """print_changelog() succesfully creates output file"""
        ofile = os.path.join(self.temp_dir, 'output.txt')
        entries = collections.OrderedDict()
        headers = []
        gcg.entrypoint.print_changelog(
            entries, headers, output_format='rpm', output_file=ofile)
        assert os.path.exists(ofile)

    # FIXME: fix this UT TO ACTUALLY VALIDATE THE OUTPUT, i think
    def test_print_changelog_use_stdout(self):
        # repo = git.Repo.init(self.tmp_dir)
        logging.debug("Go away, pylint! %s", self)
        entries = collections.OrderedDict()
        fake_commit = argparse.Namespace()
        fake_commit.date_rpm = 'baz'
        fake_commit.message = 'msg'
        fake_commit.hexsha = 'a1a2a3a4a5a6'
        entries['foo'] = [fake_commit]
        headers = {
            'foo': 'bar'
        }
        gcg.entrypoint.print_changelog(entries, headers, output_format='rpm')

        # print("OUTPUT: {}".format(mock_stdout.getvalue()))
