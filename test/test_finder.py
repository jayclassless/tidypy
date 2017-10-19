# -*- coding: utf-8 -*-

import os

from tidypy import Finder, get_default_config


def test_exclude():
    cfg = get_default_config()
    cfg['exclude'] = [
        r'invalid',
        r'\.pyc$',
    ]
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'data/broken.json',
        'data/broken.po',
        'data/broken.pot',
        'data/broken.rst',
        'data/broken.yaml',
        'input.yaml',
        'pyproject.toml',
        'setup.cfg',
        'setup.py',
        'project1/__init__.py',
        'project1/broken.py',
        'project1/koi8r.py',
        'project1/module1.py',
        'project1/utf8.py',
        'project1b/__init__.py',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.files()
    ])

    assert expected == actual


def test_files_filter():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'setup.py',
        'project1/__init__.py',
        'project1/broken.py',
        'project1/koi8r.py',
        'project1/module1.py',
        'project1/utf8.py',
        'project1b/__init__.py',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.files(filters=[r'\.py$'])
    ])

    assert expected == actual


def test_directories():
    cfg = get_default_config()
    cfg['exclude'] = ['project1b']
    finder = Finder('test/project1', cfg)

    expected = sorted([
        '.',
        'data',
        'project1',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.directories()
    ])

    assert expected == actual


def test_directories_filters():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'data',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.directories(filters=[r'data'])
    ])

    assert expected == actual


def test_directories_containing():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'project1',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.directories(containing=[r'module1.py'])
    ])

    assert expected == actual


def test_packages():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'project1',
        'project1b',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.packages()
    ])

    assert expected == actual


def test_packages_filters():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'project1',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.packages(filters=[r'1$'])
    ])

    assert expected == actual


def test_modules():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'project1/__init__.py',
        'project1/broken.py',
        'project1/koi8r.py',
        'project1/module1.py',
        'project1/utf8.py',
        'project1b/__init__.py',
        'setup.py'
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.modules()
    ])

    assert expected == actual


def test_modules_filters():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        'project1/module1.py',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.modules(filters=[r'module1'])
    ])

    assert expected == actual


def test_topmost_directories():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        '/foo/bar',
        '/else/where',
    ])

    actual = sorted(finder.topmost_directories([
        '/foo/bar',
        '/foo/bar/baz',
        '/foo/bar/blah',
        '/foo/bar/blah/a/b',
        '/else/where'
    ]))

    assert expected == actual
    assert finder.topmost_directories([]) == []
    assert finder.topmost_directories(None) == []


def test_sys_paths():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = sorted([
        '.',
    ])

    actual = sorted([
        os.path.relpath(f, 'test/project1')
        for f in finder.sys_paths()
    ])

    assert expected == actual


def test_read_file():
    cfg = get_default_config()
    finder = Finder('test/project1', cfg)

    expected = "# -*- coding: utf-8 -*-\n\ntest = 'ҖՄڇឈ'\n\n"
    assert expected == finder.read_file('test/project1/project1/utf8.py')

    expected = "# -*- coding: koi8-r -*-\n\ntest = '©©© ©©©©©© ©©©©©©©©©©©'\n\n"
    assert expected == finder.read_file('test/project1/project1/koi8r.py')

