
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['github']
    assert extender.can_handle('github:foobar/abc123') == True

    assert extender.can_handle('github:abc123') == False
    assert extender.can_handle('github-gist:abc123') == False
    assert extender.can_handle('github-gist:foobar/abc123') == False


RESP_BASIC = {
  "name": "tidypy",
  "path": "tidypy",
  "sha": "0320aacd925b1b52a5b5bfb4e0e8b51e26ab530e",
  "size": 48,
  "url": "https://api.github.com/repos/jayclassless/tidypy_extender_test/contents/tidypy?ref=master",
  "html_url": "https://github.com/jayclassless/tidypy_extender_test/blob/master/tidypy",
  "git_url": "https://api.github.com/repos/jayclassless/tidypy_extender_test/git/blobs/0320aacd925b1b52a5b5bfb4e0e8b51e26ab530e",
  "download_url": "https://raw.githubusercontent.com/jayclassless/tidypy_extender_test/master/tidypy",
  "type": "file",
  "content": "W3RpZHlweV0KdGVzdCA9ICdleHRlbmRlZCcKZXh0ZW5zaW9uID0gJ2dpdGh1\nYicK\n",
  "encoding": "base64",
  "_links": {
    "self": "https://api.github.com/repos/jayclassless/tidypy_extender_test/contents/tidypy?ref=master",
    "git": "https://api.github.com/repos/jayclassless/tidypy_extender_test/git/blobs/0320aacd925b1b52a5b5bfb4e0e8b51e26ab530e",
    "html": "https://github.com/jayclassless/tidypy_extender_test/blob/master/tidypy"
  }
}

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/repos/jayclassless/tidypy_extender_test/contents/tidypy', json=RESP_BASIC)
        extender = get_extenders()['github']
        cfg = extender.retrieve('github:jayclassless/tidypy_extender_test', 'test')

        assert cfg == {
            'extension': 'github',
            'test': 'extended',
        }


RESP_MISSING = {}

def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://api.github.com/repos/jayclassless/doesntexist/contents/tidypy', json=RESP_MISSING, status_code=404)
        m.get('https://api.github.com/repos/jayclassless/doesntexist/contents/pyproject.toml', json=RESP_MISSING, status_code=404)
        extender = get_extenders()['github']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('github:jayclassless/doesntexist', 'test')

