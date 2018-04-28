
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^pastebin:(?P<code>.+)$')


class PastebinExtender(Extender):
    """
    Retrieves configurations from public pastebin.com Pastes.
    """

    @classmethod
    def can_handle(cls, location):
        if RE_LOCATION.match(location):
            return True
        return False

    @classmethod
    def retrieve(cls, location, project_path):
        parts = RE_LOCATION.match(location).groupdict()

        resp = get_requests().get(
            'https://pastebin.com/raw/%s' % (parts['code'],),
            allow_redirects=False,
        )

        if resp.status_code > 200:
            raise DoesNotExistError()

        return cls.parse(resp.text)

