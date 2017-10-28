from __future__ import print_function

import sys

import pytest

from tidypy import util


MERGE_LIST_TESTS = (
    (
        ['foo'],
        ['bar'],
        ['foo', 'bar'],
    ),
    (
        ['foo'],
        ['foo', 'bar'],
        ['foo', 'bar'],
    ),
)

@pytest.mark.parametrize('a,b,expected', MERGE_LIST_TESTS)
def test_merge_list(a, b, expected):
    actual = util.merge_list(a, b)
    assert id(actual) != id(a)
    assert id(actual) != id(b)
    assert actual == expected


MERGE_DICT_TESTS = (
    (
        {'foo': 1},
        {'bar': 'a'},
        False,
        {'foo': 1, 'bar': 'a'},
    ),
    (
        {'foo': {'baz': 1}, 'happy': 'sad'},
        {'foo': {'baz': 2, 'blah': True}},
        False,
        {'foo': {'baz': 2, 'blah': True}, 'happy': 'sad'},
    ),
    (
        {'foo': 1, 'baz': ['a']},
        {'bar': 'a', 'baz': ['b']},
        False,
        {'foo': 1, 'bar': 'a', 'baz': ['b']},
    ),
    (
        {'foo': 1, 'baz': ['a']},
        {'bar': 'a', 'baz': ['b']},
        True,
        {'foo': 1, 'bar': 'a', 'baz': ['a', 'b']},
    ),
)

@pytest.mark.parametrize('a,b,merge_lists,expected', MERGE_DICT_TESTS)
def test_merge_dict(a, b, merge_lists, expected):
    actual = util.merge_dict(a, b, merge_lists=merge_lists)
    assert id(actual) != id(a)
    assert id(actual) != id(b)
    assert actual == expected


def test_output_error(capsys):
    util.output_error('hello world')
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'hello world\n'


def test_sysoutcapture(capsys):
    captured = None
    with util.SysOutCapture() as cap:
        print('this is stdout')
        print('this is stderr', file=sys.stderr)
        captured = (cap.get_stdout(), cap.get_stderr())

    assert captured == ('this is stdout\n', 'this is stderr\n')

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

