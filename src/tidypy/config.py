import os
import sys

import pkg_resources
import pytoml

from six import iteritems

from .util import merge_dict, output_error


# pylint: disable=protected-access


def get_tools():
    if not hasattr(get_tools, '_CACHE'):
        get_tools._CACHE = dict()
        for entry in pkg_resources.iter_entry_points('tidypy.tools'):
            try:
                get_tools._CACHE[entry.name] = entry.load()
            except ImportError as exc:  # pragma: no cover
                output_error(
                    'Could not load tool "%s" defined by "%s": %s' % (
                        entry,
                        entry.dist,
                        exc,
                    ),
                )
    return get_tools._CACHE


def get_reports():
    if not hasattr(get_reports, '_CACHE'):
        get_reports._CACHE = dict()
        for entry in pkg_resources.iter_entry_points('tidypy.reports'):
            try:
                get_reports._CACHE[entry.name] = entry.load()
            except ImportError as exc:  # pragma: no cover
                output_error(
                    'Could not load report "%s" defined by "%s": %s' % (
                        entry,
                        entry.dist,
                        exc,
                    ),
                )
    return get_reports._CACHE


def get_default_config():
    config = {}

    for name, cls in iteritems(get_tools()):
        config[name] = cls.get_default_config()

    config.update({
        'exclude': [],
        'merge_issues': True,
        'silence_tool_crashes': False,
        'threads': 3,
        'reports': [
            {
                'type': 'console',
            },
        ],
        'disabled': [],
    })

    return config


def get_user_config():
    if sys.platform == 'win32':
        user_config = os.path.expanduser(r'~\tidypy')
    else:
        user_config = os.path.join(
            os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
            'tidypy'
        )

    if os.path.exists(user_config):
        with open(user_config, 'r') as config_file:
            config = pytoml.load(config_file).get('tidypy', {})

        return merge_dict(get_default_config(), config)

    return None


def get_local_config(project_path):
    pyproject_path = os.path.join(project_path, 'pyproject.toml')

    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as config_file:
            config = pytoml.load(config_file)
        config = config.get('tool', {}).get('tidypy', {})

        return merge_dict(get_default_config(), config)

    return None


def get_project_config(project_path):
    return get_local_config(project_path) \
        or get_user_config() \
        or get_default_config()

