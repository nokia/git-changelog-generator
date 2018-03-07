#!/usr/bin/env python2

"""
Setuptools configuration for GCG project
"""

import os
import logging
from setuptools import setup


def read(fname):
    """Load content of the file with path relative to the
    project root directory (where setup.py is). Helper.

    :param fname: file name (or path relative to the project root)
    :return: file content as a string
    """
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    retval = open(fpath).read()
    return retval


def read_list(fname):
    """Load content of the file using read() function and then split
    it into a list of lines

    :param fname: file name (or path relative to the project root)
    :return: file content as a list of strings (one string per line)
             with end of lines characters stripped off
    """
    content = read(fname)
    retval = list(filter(None, content.split('\n')))
    return retval


logging.basicConfig(level=logging.INFO)

setup(
    name='gcg',
    version=read('version.txt').strip(),
    packages=['gcg', 'tests'],
    url='https://github.com/nokia/git-changelog-generator',
    license='BSD-3-Clause',
    author='Waldek Maleska',
    author_email='waldek.maleska@nokia.com',
    description='Git Changelog Generator',
    long_description=read('README.rst'),
    tests_require=read_list('requirements_test.txt'),
    setup_requires=read_list('requirements_setup.txt'),
    entry_points={
        'console_scripts': [
            'gcg = gcg.entrypoint:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    include_package_data=True,
)
