
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
except ImportError:
    from pathlib2 import Path

import click
import pkg_resources
import pytoml
import requests
import yaml

from six import iteritems, text_type, StringIO


def merge_list(list1, list2):
    merged = list(list1)

    for value in list2:
        if value not in merged:
            merged.append(value)

    return merged


def merge_dict(dict1, dict2, merge_lists=False):
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
    click.echo(click.style(msg, fg='red'), err=True)


@contextmanager
def mod_sys_path(paths):
    old_path = sys.path
    sys.path = paths + sys.path
    try:
        yield
    finally:
        sys.path = old_path


class SysOutCapture(object):
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
        return self._stdout.getvalue()

    def get_stderr(self):
        return self._stderr.getvalue()


def compile_masks(masks):
    if not masks:
        masks = []
    elif not isinstance(masks, (list, tuple)):
        masks = [masks]

    return [
        re.compile(mask)
        for mask in masks
    ]


def matches_masks(target, masks):
    for mask in masks:
        if mask.search(target):
            return True
    return False


def render_json(obj):
    return json.dumps(obj, indent=2, separators=(',', ': '))


def render_toml(obj):
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
    return yaml.dump(
        obj,
        default_flow_style=False,
        Dumper=TidyYamlDumper,
    ).rstrip()


DEFAULT_ENCODING = 'latin-1'


if sys.version_info < (3,):
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

else:
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
    return _REQUESTS

