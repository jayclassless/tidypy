
import codecs
import json
import re
import sys
import tokenize

from collections import OrderedDict
from contextlib import contextmanager

import click
import pytoml
import yaml

from six import iteritems, text_type, StringIO


def merge_dict(dict1, dict2):
    merged = dict()
    merged.update(dict1)

    for key, value in iteritems(dict2):
        if isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
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

    def read_file(filepath):
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
    def read_file(filepath):
        try:
            with tokenize.open(filepath) as target:  # pylint: disable=no-member
                return target.read()
        except (LookupError, SyntaxError, UnicodeError):
            with open(filepath, 'r', encoding=DEFAULT_ENCODING) as target:
                return target.read()

