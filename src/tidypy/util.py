
import codecs
import json
import re
import sys
import threading
import tokenize

from collections import OrderedDict
from contextlib import contextmanager

try:
    from pathlib import Path  # pylint: disable=unused-import
except ImportError:  # pragma: PY2
    from pathlib2 import Path

import click
import pkg_resources
import pytoml
import requests
import yaml

from six import iteritems, text_type, StringIO, PY2


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

    for key, value in iteritems(dict2):
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


def render_json(obj):
    """
    Serializes the specified object to JSON.

    :param obj: the object to serialize
    :returns: str
    """

    return json.dumps(obj, indent=2, separators=(',', ': '))


def render_toml(obj):
    """
    Serializes the specified object to TOML.

    :param obj: the object to serialize
    :returns: str
    """

    return pytoml.dumps(obj)


class TidyYamlDumper(yaml.Dumper):  # pylint: disable=too-many-ancestors
    pass


def unicode_representer(dumper, ustr):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str',
        ustr,
    )


def dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        list(data.items())
    )


TidyYamlDumper.add_representer(text_type, unicode_representer)
TidyYamlDumper.add_representer(OrderedDict, dict_representer)


def render_yaml(obj):
    """
    Serializes the specified object to YAML.

    :param obj: the object to serialize
    :returns: str
    """

    return yaml.dump(
        obj,
        default_flow_style=False,
        Dumper=TidyYamlDumper,
    ).rstrip()


DEFAULT_ENCODING = 'latin-1'


if PY2:  # pragma: PY2
    RE_ENCODING = re.compile(
        r'^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)',
    )

    def _read_file(filepath):
        encoding = DEFAULT_ENCODING
        with open(filepath, 'r') as target:
            i = 0
            while i < 2:
                line = target.readline()
                match = RE_ENCODING.match(line)
                if match:
                    encoding = match.groups()[0]
                    break
                i += 1

        with codecs.open(filepath, 'r', encoding=encoding) as target:
            return target.read().encode('utf-8')

else:  # pragma: PY3
    def _read_file(filepath):
        try:
            # pylint: disable=no-member
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

    :param filepath: the file to read.
    :type filepath: str
    :returns: str
    """

    with _FILE_CACHE_LOCK:
        if filepath not in _FILE_CACHE:
            _FILE_CACHE[filepath] = _read_file(filepath)
    return _FILE_CACHE[filepath]


_REQUESTS = requests.Session()
_REQUESTS.headers.update({
    'User-Agent': 'TidyPy/%s' % (
        pkg_resources.get_distribution('tidypy').version,
    ),
})


def get_requests():
    """Retrieves a ``requests`` object to use within TidyPy."""

    return _REQUESTS

