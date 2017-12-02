import base64
import os.path
import sys

import pytest
import six
import requests_mock

from tidypy import (
    get_tools,
    get_reports,
    get_extenders,
    get_default_config,
    get_user_config,
    get_local_config,
    get_project_config,
    purge_config_cache,
    DoesNotExistError,
)
from tidypy.config import put_config_cache, get_config_cache


def test_get_tools():
    expected = sorted([
        '2to3',
        'bandit',
        'eradicate',
        'jsonlint',
        'polint',
        'pycodestyle',
        'pydocstyle',
        'pyflakes',
        'pylint',
        'pyroma',
        'mccabe',
        'rstlint',
        'vulture',
        'yamllint',
    ])

    actual = get_tools()
    assert expected == sorted(actual.keys())

    actual2 = get_tools()
    assert expected == sorted(actual2.keys())
    assert id(actual) == id(actual2)


def test_get_reports():
    expected = sorted([
        'console',
        'csv',
        'json',
        'null',
        'pycodestyle',
        'pylint',
        'toml',
        'yaml',
    ])

    actual = get_reports()
    assert expected == sorted(actual.keys())

    actual2 = get_reports()
    assert expected == sorted(actual2.keys())
    assert id(actual) == id(actual2)


def test_get_extenders():
    expected = sorted([
        'github',
        'github-gist',
        'bitbucket',
        'bitbucket-snippet',
        'gitlab',
        'gitlab-snippet',
        'pastebin',
    ])

    actual = get_extenders()
    assert expected == sorted(actual.keys())

    actual2 = get_extenders()
    assert expected == sorted(actual2.keys())
    assert id(actual) == id(actual2)


def test_get_default_config():
    actual = get_default_config()
    assert actual['exclude'] == []
    assert actual['merge-issues'] == True
    assert isinstance(actual['workers'], int)
    assert actual['workers'] >= 1
    assert actual['workers'] <= 4
    assert actual['reports'] == [{'type': 'console'}]
    assert actual['disabled'] == []
    assert actual['noqa'] == True
    assert actual['extends'] == []
    assert actual['ignore-missing-extends'] == False

    for tool in get_tools().keys():
        assert tool in actual


def test_get_user_config_win(tmpdir, monkeypatch):
    project_dir = tmpdir.mkdir('project')
    user_dir = tmpdir.mkdir('win')
    config_file = user_dir.join('tidypy')
    config_file.write('[tidypy]\ntest = 1')
    monkeypatch.setattr(sys, 'platform', 'win32')
    def mockreturn(path):
        return str(config_file)
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    actual = get_user_config(str(project_dir))
    assert actual['test'] == 1


def test_get_user_config_other(tmpdir, monkeypatch):
    project_dir = tmpdir.mkdir('project')
    user_dir = tmpdir.mkdir('nix')
    user_dir.join('tidypy').write('[tidypy]\ntest = 2')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(user_dir))

    actual = get_user_config(str(project_dir))
    assert actual['test'] == 2


def test_get_user_config_missing(tmpdir, monkeypatch):
    project_dir = tmpdir.mkdir('project')
    user_dir = tmpdir.mkdir('missing')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    actual = get_user_config(str(project_dir))
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
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write('[tool.tidypy]\ntest = 5')

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 5


def test_get_project_config_user(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    user_dir.join('tidypy').write('[tidypy]\ntest = 4')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(user_dir))

    local_dir = tmpdir.mkdir('local')

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 4


def test_get_project_config_default(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')

    actual = get_project_config(str(local_dir))
    assert actual == get_default_config()


def test_extends_default(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = ['secondary.conf']\ntest = 'base'\nbase = 'foo'\nalist=['a']")
    local_dir.join('secondary.conf').write("[tidypy]\ntest = 'extended'\nextension = 'bar'\nextends = ['deepextends']\nalist=['b','c']")

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 'base'
    assert actual['base'] == 'foo'
    assert actual['extension'] == 'bar'
    assert actual['extends'] == ['secondary.conf']
    assert actual['alist'] == ['b', 'c', 'a']


RESP_FAKE = {
  "name": "tidypy",
  "path": "tidypy",
  "type": "file",
  "content": base64.b64encode(b"[tidypy]\ntest = 'extended2'\nextension2 = 'baz'").decode(),
  "encoding": "base64",
}

def test_extends_multiple(tmpdir, monkeypatch):
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/repos/fake/project/contents/tidypy', json=RESP_FAKE)

        user_dir = tmpdir.mkdir('nix')
        monkeypatch.setattr(sys, 'platform', 'darwin')
        def mockreturn(path):
            return path.replace('~', str(user_dir))
        monkeypatch.setattr(os.path, 'expanduser', mockreturn)

        local_dir = tmpdir.mkdir('local')
        local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = ['secondary.conf', 'github:fake/project']\ntest = 'base'\nbase = 'foo'")
        local_dir.join('secondary.conf').write("[tidypy]\ntest = 'extended'\nextension = 'bar'\nextends = ['deepextends']")

        actual = get_project_config(str(local_dir))
        assert actual['test'] == 'base'
        assert actual['base'] == 'foo'
        assert actual['extension'] == 'bar'
        assert actual['extension2'] == 'baz'
        assert actual['extends'] == ['secondary.conf', 'github:fake/project']


def test_extends_cache(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = 'secondary.conf'\ntest = 'base'\nbase = 'foo'")
    local_dir.join('secondary.conf').write("[tidypy]\ntest = 'extended'\nextension = 'bar'")
    put_config_cache(
        'secondary.conf',
        {
            'tidypy': {
                'test': 'cached extended',
                'extension': 'cached bar',
            },
        },
    )

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 'base'
    assert actual['base'] == 'foo'
    assert actual['extension'] == 'cached bar'

    actual = get_project_config(str(local_dir), use_cache=False)
    assert actual['test'] == 'base'
    assert actual['base'] == 'foo'
    assert actual['extension'] == 'bar'


def test_extends_cache_win(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('win').join('tidypy')
    monkeypatch.setattr(sys, 'platform', 'win32')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = 'secondary.conf'\ntest = 'base'\nbase = 'foo'")
    local_dir.join('secondary.conf').write("[tidypy]\ntest = 'extended'\nextension = 'bar'")
    put_config_cache(
        'secondary.conf',
        {
            'tidypy': {
                'test': 'cached extended',
                'extension': 'cached bar',
            },
        },
    )

    actual = get_project_config(str(local_dir))
    assert actual['test'] == 'base'
    assert actual['base'] == 'foo'
    assert actual['extension'] == 'cached bar'


def test_extends_missing(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    local_dir = tmpdir.mkdir('local')
    local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = ['doesntexist.conf']")

    with pytest.raises(DoesNotExistError):
        get_project_config(str(local_dir))

    local_dir.join('pyproject.toml').write("[tool.tidypy]\nextends = ['doesntexist.conf']\nignore-missing-extends = true")

    actual = get_project_config(str(local_dir))
    assert actual['extends'] == ['doesntexist.conf']


def test_purge_config_cache(tmpdir, monkeypatch):
    user_dir = tmpdir.mkdir('nix')
    monkeypatch.setattr(sys, 'platform', 'darwin')
    def mockreturn(path):
        return path.replace('~', str(user_dir))
    monkeypatch.setattr(os.path, 'expanduser', mockreturn)

    put_config_cache('foo', {'tidypy': {'foo': 1}})
    put_config_cache('bar', {'tidypy': {'bar': 1}})

    assert get_config_cache('foo') == {'foo': 1}
    assert get_config_cache('bar') == {'bar': 1}

    purge_config_cache('foo')

    assert get_config_cache('foo') is None
    assert get_config_cache('bar') == {'bar': 1}

    purge_config_cache()

    assert get_config_cache('foo') is None
    assert get_config_cache('bar') is None

