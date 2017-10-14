import pytest

from tidypy import util


MERGE_DICT_TESTS = (
    (
        {'foo': 1},
        {'bar': 'a'},
        {'foo': 1, 'bar': 'a'},
    ),
    (
        {'foo': {'baz': 1}, 'happy': 'sad'},
        {'foo': {'baz': 2, 'blah': True}},
        {'foo': {'baz': 2, 'blah': True}, 'happy': 'sad'},
    ),
)

@pytest.mark.parametrize('a,b,expected', MERGE_DICT_TESTS)
def test_merge_dict(a, b, expected):
    actual = util.merge_dict(a, b)
    assert id(actual) != id(a)
    assert id(actual) != id(b)
    assert actual == expected


def test_output_error(capsys):
    util.output_error('hello world')
    out, err = capsys.readouterr()
    assert out == ''
    assert err == 'hello world\n'

