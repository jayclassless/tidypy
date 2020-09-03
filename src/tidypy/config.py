import multiprocessing
import os
import shutil
import sys

from hashlib import sha512

import toml
import pkg_resources

from .extenders import DoesNotExistError
from .extenders.filesys import FilesysExtender
from .util import merge_dict, output_error


def get_tools():
    """
    Retrieves the TidyPy tools that are available in the current Python
    environment.

    The returned dictionary has keys that are the tool names and values are the
    tool classes.

    :rtype: dict
    """

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
    """
    Retrieves the TidyPy issue reports that are available in the current Python
    environment.

    The returned dictionary has keys are the report names and values are the
    report classes.

    :rtype: dict
    """

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
    """
    Retrieves the TidyPy configuration extenders that are available in the
    current Python environment.

    The returned dictionary has keys are the extender names and values are the
    extender classes.

    :rtype: dict
    """

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
    """
    Clears out the cache of TidyPy configurations that were retrieved from
    outside the normal locations.
    """

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
            config = toml.load(config_file).get('tidypy', {})

    return config


def put_config_cache(location, config):
    path = get_cache_path(location)
    with open(path, 'w') as config_file:
        toml.dump(config, config_file)


def retrieve_extension(location, project_path, use_cache=True):
    if use_cache:
        config = get_config_cache(location)
        if config is not None:
            return config

    extender = FilesysExtender
    for cls in get_extenders().values():
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
    if isinstance(extends, str):
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
    """
    Produces a stock/out-of-the-box TidyPy configuration.

    :rtype: dict
    """

    config = {}

    for name, cls in get_tools().items():
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
        'disabled': [],
        'noqa': True,
        'extends': [],
        'ignore-missing-extends': False,
    })

    return config


def get_specific_config(config_file_path, project_path, use_cache=True):
    """
    Produces a TidyPy configuration from the specified file.

    :param config_file_path: the file containing a TidyPy configuration
    :type config_file_path: str
    :param project_path: the path to the project that is going to be analyzed
    :type project_path: str
    :param use_cache:
        whether or not to use cached versions of any remote/referenced TidyPy
        configurations. If not specified, defaults to ``True``.
    :type use_cache: bool
    :rtype: dict
    """

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = toml.load(config_file)
            if 'tidypy' in config:
                # Originally unintended, but we'll support configuration files
                # where everything in scoped in a "tidypy" table.
                config = config['tidypy']

        config = merge_dict(get_default_config(), config)
        config = process_extensions(config, project_path, use_cache=use_cache)
        return config

    return None


def get_user_config(project_path, use_cache=True):
    """
    Produces a TidyPy configuration that incorporates the configuration files
    stored in the current user's home directory.

    :param project_path: the path to the project that is going to be analyzed
    :type project_path: str
    :param use_cache:
        whether or not to use cached versions of any remote/referenced TidyPy
        configurations. If not specified, defaults to ``True``.
    :type use_cache: bool
    :rtype: dict
    """

    if sys.platform == 'win32':
        user_config = os.path.expanduser(r'~\\tidypy')
    else:
        user_config = os.path.join(
            os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
            'tidypy'
        )

    return get_specific_config(user_config, project_path, use_cache=use_cache)


def get_local_config(project_path, use_cache=True):
    """
    Produces a TidyPy configuration using the ``pyproject.toml`` in the
    project's directory.

    :param project_path: the path to the project that is going to be analyzed
    :type project_path: str
    :param use_cache:
        whether or not to use cached versions of any remote/referenced TidyPy
        configurations. If not specified, defaults to ``True``.
    :type use_cache: bool
    :rtype: dict
    """

    pyproject_path = os.path.join(project_path, 'pyproject.toml')

    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as config_file:
            config = toml.load(config_file)

        config = config.get('tool', {}).get('tidypy', {})
        config = merge_dict(get_default_config(), config)
        config = process_extensions(config, project_path, use_cache=use_cache)
        return config

    return None


def get_project_config(project_path, use_cache=True):
    """
    Produces the Tidypy configuration to use for the specified project.

    If a ``pyproject.toml`` exists, the configuration will be based on that. If
    not, the TidyPy configuration in the user's home directory will be used. If
    one does not exist, the default configuration will be used.

    :param project_path: the path to the project that is going to be analyzed
    :type project_path: str
    :param use_cache:
        whether or not to use cached versions of any remote/referenced TidyPy
        configurations. If not specified, defaults to ``True``.
    :type use_cache: bool
    :rtype: dict
    """

    return get_local_config(project_path, use_cache=use_cache) \
        or get_user_config(project_path, use_cache=use_cache) \
        or get_default_config()

