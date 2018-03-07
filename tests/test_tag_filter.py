#!/usr/bin/env python2
"""
Unit tests for version validation and matching
"""

from gcg.tag_filter import TagFilter


def test_semantic_version_ok():
    """Various correct semantic version strings"""
    obj = TagFilter()
    assert obj.matches('1.2.0')
    assert obj.matches('1.2.0-3')
    assert obj.matches('foo1.2.0', prefix='foo')

    assert TagFilter(prefix='v').matches('v1.2.0')
    assert TagFilter(prefix='foo').matches('foo1.2.0')


def test_semantic_version_failures():
    """Various invalid semantic version strings, or with invalid
    prefix"""
    obj = TagFilter()
    assert not obj.matches('foo1.2.0', prefix='oof')
    assert not obj.matches('1')
    assert not obj.matches('1.2')
    assert not obj.matches('v1.2.3')


def test_custom_tag_pattern_success():
    """
    Simple success scenarios
    """
    assert TagFilter(r'v(\d+)\.(\d+)').matches('v123.123')
    assert TagFilter('v(\\d+)\\.(\\d+)').matches('v123.123')


def test_custom_tag_pattern_fails():
    """Simple failing scenarios"""
    assert not TagFilter(r'^(\d+)\.(\d+)$').matches('v123.123')
    assert not TagFilter(r'^(\d+)\.(\d+)$').matches('1.2.3')


def test_prefix_is_optional():
    """Lack of prefix is still considered a valid version"""
    assert TagFilter(prefix='foo').matches('foo1.2.0')
    assert TagFilter(r'^(\d+)\.(\d+)$', 'v').matches('v123.123')


def test_filter_semvers_only():
    """Test only semver-compliant versions are returned by only_semvers"""
    input_list = [
        'v1.2',
        '1.4',
        '0.1.2',
        '99.88.77-654321',
        '22.33.1-YADA',
        '1.2.3_5',
    ]
    expected = [
        '0.1.2',
        '99.88.77-654321',
        '22.33.1-YADA',
    ]
    assert expected == TagFilter().matching_only(input_list)


def test_matching_only_with_prefix():
    """Test only semver-compliant versions are returned by only_semvers
    while using a prefix. The prefix is optional."""
    input_list = [
        'v1.2',
        '1.4',
        '0.1.2',
        'v0.1.2',
        'v99.88.77-654321',
        '22.33.1-YADA',
        '1.2.3_5',
    ]
    expected = [
        '0.1.2',
        'v0.1.2',
        'v99.88.77-654321',
        '22.33.1-YADA',
    ]
    assert expected == TagFilter(prefix='v').matching_only(input_list)
    assert expected == TagFilter().matching_only(input_list, prefix='v')


def test_matching_only_custom():
    """
    Filter out unwanted items from the list, with and without
    the prefix
    """

    assert TagFilter(r'^(\d+)\.(\d+)$').matching_only([
        'v123.123',
        '01.02',
        '1.2.3',
        '1.2.3-4+bld5']) == ['01.02']

    assert TagFilter(r'^(\d+)\.(\d+)$', prefix='v').matching_only([
        'v123.123',
        '01.02',
        '1.2.3',
        '1.2.3-4+bld5']) == ['v123.123', '01.02']
