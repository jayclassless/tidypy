
import ast
import re
import sys
import threading
import tokenize

from contextlib import contextmanager
from io import StringIO

import click
import pkg_resources
import requests


def merge_list(list1, list2):
    """
    Merges the contents of two lists into a new list.

    :param list1: the first list
    :type list1: list
    :param list2: the second list
    :type list2: list
    :returns: list
    """

    merged = list(list1)

    for value in list2:
        if value not in merged:
            merged.append(value)

    return merged


def merge_dict(dict1, dict2, merge_lists=False):
    """
    Recursively merges the contents of two dictionaries into a new dictionary.

    When both input dictionaries share a key, the value from ``dict2`` is
    kept.

    :param dict1: the first dictionary
    :type dict1: dict
    :param dict2: the second dictionary
    :type dict2: dict
    :param merge_lists:
        when this function encounters a key that contains lists in both input
        dictionaries, this parameter dictates whether or not those lists should
        be merged. If not specified, defaults to ``False``.
    :type merge_lists: bool
    :returns: dict
    """

    merged = dict(dict1)

    for key, value in dict2.items():
        if isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        elif merge_lists and isinstance(merged.get(key), list):
            merged[key] = merge_list(merged[key], value)
        else:
            merged[key] = value

    return merged


def output_error(msg):
    """
    Prints the specified string to ``stderr``.

    :param msg: the message to print
    :type msg: str
    """

    click.echo(click.style(msg, fg='red'), err=True)


@contextmanager
def mod_sys_path(paths):
    """
    A context manager that will append the specified paths to Python's
    ``sys.path`` during the execution of the block.

    :param paths: the paths to append
    :type paths: list(str)
    """

    old_path = sys.path
    sys.path = paths + sys.path
    try:
        yield
    finally:
        sys.path = old_path


class SysOutCapture(object):
    """
    A context manager that captures output to ``stdout`` and ``stderr`` during
    the execution of the block.
    """

    def __init__(self):
        self._original_streams = None
        self._stdout = None
        self._stderr = None

    def __enter__(self):
        self._stdout = StringIO()
        self._stderr = StringIO()
        self._original_streams = (sys.stdout, sys.stderr)
        sys.stdout, sys.stderr = self._stdout, self._stderr
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout, sys.stderr = self._original_streams
        self._original_streams = None

    def get_stdout(self):
        """
        Retrieves the content that was written to ``stdout``.

        :returns: str
        """

        return self._stdout.getvalue()

    def get_stderr(self):
        """
        Retrieves the content that was written to ``stderr``.

        :returns: str
        """

        return self._stderr.getvalue()


def compile_masks(masks):
    """
    Compiles a list of regular expressions.

    :param masks: the regular expressions to compile
    :type masks: list(str) or str
    :returns: list(regular expression object)
    """

    if not masks:
        masks = []
    elif not isinstance(masks, (list, tuple)):
        masks = [masks]

    return [
        re.compile(mask)
        for mask in masks
    ]


def matches_masks(target, masks):
    """
    Determines whether or not the target string matches any of the regular
    expressions specified.

    :param target: the string to check
    :type target: str
    :param masks: the regular expressions to check against
    :type masks: list(regular expression object)
    :returns: bool
    """

    for mask in masks:
        if mask.search(target):
            return True
    return False


DEFAULT_ENCODING = 'latin-1'


def _read_file(filepath):
    try:
        with tokenize.open(filepath) as target:
            return target.read()
    except (LookupError, SyntaxError, UnicodeError):
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as target:
            return target.read()


_FILE_CACHE = {}
_FILE_CACHE_LOCK = threading.Lock()


def read_file(filepath):
    """
    Retrieves the contents of the specified file.

    This function performs simple caching so that the same file isn't read more
    than once per process.

    :param filepath: the file to read
    :type filepath: str
    :returns: str
    """

    with _FILE_CACHE_LOCK:
        if filepath not in _FILE_CACHE:
            _FILE_CACHE[filepath] = _read_file(filepath)
    return _FILE_CACHE[filepath]


_AST_CACHE = {}
_AST_CACHE_LOCK = threading.Lock()


def parse_python_file(filepath):
    """
    Retrieves the AST of the specified file.

    This function performs simple caching so that the same file isn't read or
    parsed more than once per process.

    :param filepath: the file to parse
    :type filepath: str
    :returns: ast.AST
    """

    with _AST_CACHE_LOCK:
        if filepath not in _AST_CACHE:
            source = read_file(filepath)
            _AST_CACHE[filepath] = ast.parse(source, filename=filepath)
    return _AST_CACHE[filepath]


_REQUESTS = requests.Session()
_REQUESTS.headers.update({
    'User-Agent': 'TidyPy/%s' % (
        pkg_resources.get_distribution('tidypy').version,
    ),
})


def get_requests():
    """Retrieves a ``requests`` object to use within TidyPy."""

    return _REQUESTS

