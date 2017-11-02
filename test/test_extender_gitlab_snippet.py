
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['gitlab-snippet']
    assert extender.can_handle('gitlab-snippet:abc123') == True

    assert extender.can_handle('gitlab-snippet:') == False
    assert extender.can_handle('gitlab:foobar/abc123') == False


RESP_BASIC = '''
[tidypy]
test = 'extended'
extension = 'gitlab snippet'
'''

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/snippets/1681724/raw', text=RESP_BASIC, headers={'Content-Disposition': 'inline; filename="tidypy"'})
        extender = get_extenders()['gitlab-snippet']
        cfg = extender.retrieve('gitlab-snippet:1681724', 'test')

        assert cfg == {
            'extension': 'gitlab snippet',
            'test': 'extended',
        }


RESP_PYPROJECT = '''
[tool.tidypy]
test = 'extended'
extension = 'gitlab snippet pyproject'
'''

def test_retrieve_pyproject():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/snippets/1681728/raw', text=RESP_PYPROJECT, headers={'Content-Disposition': 'inline; filename="pyproject.toml"'})
        extender = get_extenders()['gitlab-snippet']
        cfg = extender.retrieve('gitlab-snippet:1681728', 'test')

        assert cfg == {
            'extension': 'gitlab snippet pyproject',
            'test': 'extended',
        }


RESP_BADNAME = '''
[tidypy]
test = 'extended'
extension = 'gitlab snippet badname'
'''

def test_retrieve_badname():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/snippets/1681729/raw', text=RESP_BADNAME, headers={'Content-Disposition': 'inline; filename="something.conf"'})
        extender = get_extenders()['gitlab-snippet']
        cfg = extender.retrieve('gitlab-snippet:1681729', 'test')

        assert cfg == {
            'extension': 'gitlab snippet badname',
            'test': 'extended',
        }


def test_retrieve_missing_name():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/snippets/1681729/raw', text=RESP_BADNAME)
        extender = get_extenders()['gitlab-snippet']
        cfg = extender.retrieve('gitlab-snippet:1681729', 'test')

        assert cfg == {
            'extension': 'gitlab snippet badname',
            'test': 'extended',
        }


def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://gitlab.com/snippets/999999999999/raw', status_code=302, headers={'Location': 'http://fake.com/missing'})
        extender = get_extenders()['gitlab-snippet']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('gitlab-snippet:999999999999', 'test')

