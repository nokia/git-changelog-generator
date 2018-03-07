#!/usr/bin/env python2
"""
All functionality related to filtering out Git tags against
Semantic Versioning or custum rules
"""

import re
import logging
import semver


class TagFilter(object):
    """
    Class facilitating validating and filtering versions against
    SemVer rules or custom, user-provided version scheme
    """
    def __init__(self, pattern=None, prefix=None):
        self.prefix = prefix
        if pattern is None:
            self.matches = self.is_semantic_version
        else:
            self.matches = self.is_custom_version
            self.custom_pattern = re.compile(pattern)

    def is_semantic_version(self, value, prefix=None):
        """
        Verify if given value is a Semantic Version (as defined by semver.org)

        :param value: input string
        :param prefix: optional prefix (e.g. 'v') to be stripped off
                       the input string. If omitted, use prefix given
                       at object creation time.
        :return: True or False
        """
        logging.debug("Validate string '%s' against SemVer rules", value)
        version_string = self.strip_prefix(value, prefix)
        try:
            semver.parse(version_string)
        except ValueError:
            return False
        return True

    def is_custom_version(self, value, prefix=None):
        """
        Verify if given value matches a custom regular expression
        specified by a command-line option.

        :param value: input string
        :param prefix: optional prefix (e.g. 'v') to be stripped off
                       the input string
        :return: True or False
        """
        logging.debug("Validate string '%s' against custom pattern '%s'",
                      value, self.custom_pattern.pattern)
        version_string = self.strip_prefix(value, prefix)
        retval = False
        if self.custom_pattern.match(version_string):
            retval = True
        return retval

    def matching_only(self, versions, prefix=None):
        """
        Return only the list of versions (tags) that match the configured
        versioning rules

        :param versions: list of strings to check
        :param prefix: prefix of the version string; if present, will be
                       ignored before checking if string is a semantic version
        :return: list containing only those strings which match SemVer.org
                 specification; may be empty.
        """
        return [x for x in versions if
                self.matches(x, prefix=prefix)]

    def strip_prefix(self, value, prefix=None):
        """

        :param prefix: optional prefix (e.g. 'v') to be stripped off
                       the input string. If omitted, use prefix given
                       at object creation time.
        :param value: version string
        :return:
        """
        if prefix is None:
            prefix = self.prefix

        version_string = value
        if prefix and value.startswith(prefix):
            version_string = value[len(prefix):]
        return version_string
