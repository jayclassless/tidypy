
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['bitbucket']
    assert extender.can_handle('bitbucket:foobar/abc123') == True

    assert extender.can_handle('bitbucket-snippet:foobar/abc123') == False


RESP_BASIC = '''
[tidypy]
test = 'extended'
extension = 'bitbucket'
'''

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://api.bitbucket.org/2.0/repositories/jayclassless/tidypy_extender_test/src', status_code=302, headers={'Location': 'http://fake.com/test'})
        m.get('http://fake.com/test/tidypy', text=RESP_BASIC)
        extender = get_extenders()['bitbucket']
        cfg = extender.retrieve('bitbucket:jayclassless/tidypy_extender_test', 'test')

        assert cfg == {
            'extension': 'bitbucket',
            'test': 'extended',
        }


RESP_PYPROJECT = '''
[tool.tidypy]
test = 'extended'
extension = 'bitbucket snippet pyproject'
'''

def test_retrieve_pyproject():
    with requests_mock.Mocker() as m:
        m.get('https://api.bitbucket.org/2.0/repositories/jayclassless/tidypy_extender_test2/src', status_code=302, headers={'Location': 'http://fake.com/test'})
        m.get('http://fake.com/test/tidypy', status_code=404)
        m.get('http://fake.com/test/pyproject.toml', text=RESP_PYPROJECT)
        extender = get_extenders()['bitbucket']
        cfg = extender.retrieve('bitbucket:jayclassless/tidypy_extender_test2', 'test')

        assert cfg == {
            'extension': 'bitbucket snippet pyproject',
            'test': 'extended',
        }


def test_retrieve_no_good_files():
    with requests_mock.Mocker() as m:
        m.get('https://api.bitbucket.org/2.0/repositories/jayclassless/tidypy_extender_test2/src', status_code=302, headers={'Location': 'http://fake.com/test'})
        m.get('http://fake.com/test/tidypy', status_code=404)
        m.get('http://fake.com/test/pyproject.toml', status_code=404)
        extender = get_extenders()['bitbucket']

        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('bitbucket:jayclassless/tidypy_extender_test2', 'test')


def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://api.bitbucket.org/2.0/repositories/jayclassless/doesntexist/src', status_code=404)
        extender = get_extenders()['bitbucket']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('bitbucket:jayclassless/doesntexist', 'test')

