#!/usr/bin/env python2

"""Unit tests for various combinations of main() parameters"""

import logging
import shutil

import tempfile
import unittest

import git
from mock import patch

import gcg.entrypoint
import gcg.errors as err


class TestUserInputs(unittest.TestCase):
    """Unit test suite for invalid user inputs"""
    def setUp(self):
        logging.basicConfig(level=logging.FATAL)
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    @staticmethod
    def test_main_missing_debpkgname():
        """Missing package name for DEB output type"""
        assert err.INVALID_INPUT == gcg.entrypoint.main([
            'xyz', '-O', 'deb'])

    @staticmethod
    def test_main_missing_debdistro():
        """Missing debian distribution for DEB output type"""
        assert err.INVALID_INPUT == gcg.entrypoint.main([
            'xyz', '-O', 'deb', '-n', 'pkgname'])

    @staticmethod
    def test_main_repo_invalid_path():
        """Path does not exist"""
        assert err.REPO_PATH_INVALID == gcg.entrypoint.main([
            'xyz', '-p', '/doesNot3xist', '-O', 'rpm'])

    def test_main_path_is_not_repo(self):
        """A directory given is not a Git repository"""
        assert err.REPO_PATH_NOT_REPO == gcg.entrypoint.main([
            'xyz', '-p', self.tmp_dir, '-O', 'rpm'])

    @staticmethod
    @patch('git.Repo')
    def test_main_ref_inv_upper_limit(mock_git_repo):
        """Invalid upper limit specified by reference"""
        mock_git_repo().commit.side_effect = git.BadName('Bang')
        assert err.INVALID_VCS_LIMITS == gcg.entrypoint.main([
            'xyz', '--until', 'NonExistantTag', '-O', 'rpm'])

    @staticmethod
    @patch('git.Repo')
    def test_main_sha_inv_upper_limit(mock_git_repo):
        """Invalid upper limit specified by commit hash"""
        mock_git_repo().commit.side_effect = ValueError('Boom')
        assert err.INVALID_VCS_LIMITS == gcg.entrypoint.main([
            'xyz', '--until', 'a1a2a2a3a4a5a6a', '-O', 'rpm'])

    @staticmethod
    @patch('git.Repo')
    def test_main_ref_inv_low_limit(mock_git_repo):
        """Invalid lower limit specified by reference"""
        mock_git_repo().commit.side_effect = git.BadName('Bang')
        assert err.INVALID_VCS_LIMITS == gcg.entrypoint.main([
            'xyz', '--since', 'NonExistantTag', '-O', 'rpm'])

    @staticmethod
    @patch('git.Repo')
    def test_main_sha_inv_low_limit(mock_git_repo):
        """Invalid lower limit specified by commit hash"""
        mock_git_repo().commit.side_effect = ValueError('Boom')
        assert err.INVALID_VCS_LIMITS == gcg.entrypoint.main([
            'xyz', '--since', 'a1a2a2a3a4a5a6a', '-O', 'rpm'])
