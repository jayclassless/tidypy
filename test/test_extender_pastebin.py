
import requests_mock
import pytest

from tidypy import get_extenders, DoesNotExistError


def test_can_handle():
    extender = get_extenders()['pastebin']
    assert extender.can_handle('pastebin:abc123') == True

    assert extender.can_handle('pastebin:') == False


RESP_BASIC = '''
[tidypy]
test = 'extended'
extension = 'pastebin'
'''

def test_retrieve_basic():
    with requests_mock.Mocker() as m:
        m.get('https://pastebin.com/raw/MYyLRaaB', text=RESP_BASIC)
        extender = get_extenders()['pastebin']
        cfg = extender.retrieve('pastebin:MYyLRaaB', 'test')

        assert cfg == {
            'extension': 'pastebin',
            'test': 'extended',
        }


def test_retrieve_missing():
    with requests_mock.Mocker() as m:
        m.get('https://pastebin.com/raw/doesntexist', status_code=302, headers={'Location': 'http://fake.com/missing'})
        extender = get_extenders()['pastebin']
        with pytest.raises(DoesNotExistError):
            cfg = extender.retrieve('pastebin:doesntexist', 'test')

