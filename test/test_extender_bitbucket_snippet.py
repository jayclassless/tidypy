
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['bitbucket-snippet']
    assert extender.can_handle('bitbucket-snippet:foobar/abc123') == True

    assert extender.can_handle('bitbucket:foobar/abc123') == False


RESP_BASIC = '''
[tidypy]
test = 'extended'
extension = 'bitbucket snippet'
'''

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://bitbucket.org/api/2.0/snippets/jayclassless/74zBE6/files/tidypy', text=RESP_BASIC)
        extender = get_extenders()['bitbucket-snippet']
        cfg = extender.retrieve('bitbucket-snippet:jayclassless/74zBE6', 'test')

        assert cfg == {
            'extension': 'bitbucket snippet',
            'test': 'extended',
        }


RESP_PYPROJECT = '''
[tool.tidypy]
test = 'extended'
extension = 'bitbucket snippet pyproject'
'''

def test_retrieve_pyproject():
    with requests_mock.Mocker() as m:
        m.get('https://bitbucket.org/api/2.0/snippets/jayclassless/q4zzyR/files/tidypy', status_code=302, headers={'Location': 'https://fake.com/missing'})
        m.get('https://bitbucket.org/api/2.0/snippets/jayclassless/q4zzyR/files/pyproject.toml', text=RESP_PYPROJECT)
        m.get('https://fake.com/missing', status_code=404)
        extender = get_extenders()['bitbucket-snippet']
        cfg = extender.retrieve('bitbucket-snippet:jayclassless/q4zzyR', 'test')

        assert cfg == {
            'extension': 'bitbucket snippet pyproject',
            'test': 'extended',
        }


def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://bitbucket.org/api/2.0/snippets/jayclassless/doesntexist/files/tidypy', status_code=302, headers={'Location': 'https://fake.com/missing'})
        m.get('https://bitbucket.org/api/2.0/snippets/jayclassless/doesntexist/files/pyproject.toml', status_code=302, headers={'Location': 'https://fake.com/missing'})
        m.get('https://fake.com/missing', status_code=404)
        extender = get_extenders()['bitbucket-snippet']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('bitbucket-snippet:jayclassless/doesntexist', 'test')

