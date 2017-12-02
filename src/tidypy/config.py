import multiprocessing
import os
import shutil
import sys

from hashlib import sha512

import pkg_resources
import pytoml

from six import iteritems, itervalues, string_types

from .extenders import DoesNotExistError
from .extenders.filesys import FilesysExtender
from .util import merge_dict, output_error


def get_tools():
    # pylint: disable=protected-access

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
    # pylint: disable=protected-access

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


def get_extenders():
    # pylint: disable=protected-access

    if not hasattr(get_extenders, '_CACHE'):
        get_extenders._CACHE = dict()
        for entry in pkg_resources.iter_entry_points('tidypy.extenders'):
            try:
                get_extenders._CACHE[entry.name] = entry.load()
            except ImportError as exc:  # pragma: no cover
                output_error(
                    'Could not load extender "%s" defined by "%s": %s' % (
                        entry,
                        entry.dist,
                        exc,
                    ),
                )
    return get_extenders._CACHE


def get_cache_path(location=None):
    if sys.platform == 'win32':
        cache_dir = os.path.expanduser(r'~\tidypy_cache')
    else:
        cache_dir = os.path.join(
            os.getenv('XDG_CACHE_HOME') or os.path.expanduser('~/.cache'),
            'tidypy'
        )

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if location:
        location = location.encode('utf-8')
        return os.path.join(cache_dir, sha512(location).hexdigest())

    return cache_dir


def purge_config_cache(location=None):
    cache_path = get_cache_path(location)

    if location:
        os.remove(cache_path)
    else:
        shutil.rmtree(cache_path)


def get_config_cache(location):
    config = None

    path = get_cache_path(location)
    if os.path.exists(path):
        with open(path, 'r') as config_file:
            config = pytoml.load(config_file).get('tidypy', {})

    return config


def put_config_cache(location, config):
    path = get_cache_path(location)
    with open(path, 'w') as config_file:
        pytoml.dump(config, config_file)


def retrieve_extension(location, project_path, use_cache=True):
    if use_cache:
        config = get_config_cache(location)
        if config is not None:
            return config

    extender = FilesysExtender
    for cls in itervalues(get_extenders()):
        if cls.can_handle(location):
            extender = cls
            break

    config = extender.retrieve(location, project_path)
    if 'extends' in config:
        del config['extends']

    if use_cache:
        put_config_cache(location, config)

    return config


def process_extensions(config, project_path, use_cache=True):
    extends = config['extends']
    if not extends:
        return config
    if isinstance(extends, string_types):
        extends = [extends]

    base = dict()
    for location in extends:
        try:
            ext_config = retrieve_extension(
                location,
                project_path,
                use_cache=use_cache,
            )
        except DoesNotExistError:
            if not config['ignore-missing-extends']:
                raise
        else:
            base = merge_dict(base, ext_config, merge_lists=True)

    return merge_dict(base, config, merge_lists=True)


def get_default_config():
    config = {}

    for name, cls in iteritems(get_tools()):
        config[name] = cls.get_default_config()

    try:
        workers = multiprocessing.cpu_count() - 1
    except NotImplementedError:  # pragma: no cover
        workers = 1
    workers = max(1, min(4, workers))

    config.update({
        'exclude': [],
        'merge-issues': True,
        'workers': workers,
        'reports': [
            {
                'type': 'console',
            },
        ],
        'disabled': [],
        'noqa': True,
        'extends': [],
        'ignore-missing-extends': False,
    })

    return config


def get_user_config(project_path, use_cache=True):
    if sys.platform == 'win32':
        user_config = os.path.expanduser(r'~\\tidypy')
    else:
        user_config = os.path.join(
            os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
            'tidypy'
        )

    if os.path.exists(user_config):
        with open(user_config, 'r') as config_file:
            config = pytoml.load(config_file).get('tidypy', {})

        config = merge_dict(get_default_config(), config)
        config = process_extensions(config, project_path, use_cache=use_cache)
        return config

    return None


def get_local_config(project_path, use_cache=True):
    pyproject_path = os.path.join(project_path, 'pyproject.toml')

    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as config_file:
            config = pytoml.load(config_file)

        config = config.get('tool', {}).get('tidypy', {})
        config = merge_dict(get_default_config(), config)
        config = process_extensions(config, project_path, use_cache=use_cache)
        return config

    return None


def get_project_config(project_path, use_cache=True):
    return get_local_config(project_path, use_cache=use_cache) \
        or get_user_config(project_path, use_cache=use_cache) \
        or get_default_config()

