import os.path
import sys

from tidypy import (
    get_tools,
    get_reports,
    get_default_config,
    get_user_config,
    get_local_config,
    get_project_config,
)


def test_get_tools():
    expected = [
        'bandit',
        'eradicate',
        'jsonlint',
        'polint',
        'pycodestyle',
        'pydocstyle',
        'pyflakes',
        'pylint',
        'pyroma',
        'radon',
        'rstlint',
        'vulture',
        'yamllint',
    ]

    actual = get_tools()
    assert expected == sorted(actual.keys())

    actual2 = get_tools()
    assert expected == sorted(actual2.keys())
    assert id(actual) == id(actual2)


def test_get_reports():
    expected = [
        'console',
        'csv',
        'json',
        'null',
        'pycodestyle',
        'pylint',
        'toml',
        'yaml',
    ]
    actual = get_reports()
    assert expected == sorted(actual.keys())

    actual2 = get_reports()
    assert expected == sorted(actual2.keys())
    assert id(actual) == id(actual2)


def test_get_default_config():
    actual = get_default_config()
    assert actual['exclude'] == []
    assert actual['merge_issues'] == True
    assert actual['silence_tool_crashes'] == False
    assert actual['threads'] == 3
    assert actual['reports'] == [{'type': 'console'}]
    assert actual['disabled'] == []

    for tool in get_tools().keys():
        assert tool in actual


def test_get_user_config_win(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('win').join('tidypy')
    user_dir.write('[tidypy]\ntest = 1')
    monkeypatch.setattr(sys, 'platform', 'win32')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    actual = get_user_config()
    assert actual['test'] == 1


def test_get_user_config_other(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    user_dir.join('tidypy').write('[tidypy]\ntest = 2')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    actual = get_user_config()
    assert actual['test'] == 2


def test_get_user_config_missing(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('missing')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    actual = get_user_config()
    assert actual == None


def test_get_local_config(tmpdir):
    local_dir = tmpdir.mkdir('missing')
    local_dir.join('pyproject.toml').write('[tool.tidypy]\ntest = 3')

    actual = get_local_config(str(local_dir))
    assert actual['test'] == 3


def test_get_local_config_missing(tmpdir, monkeypatch):
    local_dir = tmpdir.mkdir('missing')

    actual = get_local_config(str(local_dir))
    assert actual == None


def test_get_project_config_local(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    user_dir.join('tidypy').write('[tidypy]\ntest = 4')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write('[tool.tidypy]\ntest = 5')

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 5


def test_get_project_config_user(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    user_dir.join('tidypy').write('[tidypy]\ntest = 4')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 4


def test_get_project_config_default(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return str(user_dir)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')

    actual = get_project_config(str(local_dir))
    assert actual == get_default_config()

