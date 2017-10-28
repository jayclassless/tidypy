
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['gitlab']
    assert extender.can_handle('gitlab:foobar/abc123') == True

    assert extender.can_handle('gitlab:') == False
    assert extender.can_handle('gitlab:abc123') == False
    assert extender.can_handle('gitlab-snippet:abc123') == False


RESP_BASIC = '''
[tidypy]
test = 'extended'
extension = 'gitlab'
'''

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/jayclassless/tidypy_extender_test/raw/master/tidypy', text=RESP_BASIC)
        extender = get_extenders()['gitlab']
        cfg = extender.retrieve('gitlab:jayclassless/tidypy_extender_test', 'test')

        assert cfg == {
            'extension': 'gitlab',
            'test': 'extended',
        }


def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/jayclassless/doesntexist/raw/master/tidypy', status_code=302, headers={'Location': 'http://fake.com/missing'})
        m.get('https://gitlab.com/jayclassless/doesntexist/raw/master/pyproject.toml', status_code=302, headers={'Location': 'http://fake.com/missing'})
        extender = get_extenders()['gitlab']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('gitlab:jayclassless/doesntexist', 'test')

