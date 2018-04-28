
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^bitbucket:(?P<owner>[^/]+)/(?P<code>.+)$')


class BitbucketExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    Bitbucket repositories.
    """

    @classmethod
    def can_handle(cls, location):
        if RE_LOCATION.match(location):
            return True
        return False

    @classmethod
    def retrieve(cls, location, project_path):
        parts = RE_LOCATION.match(location).groupdict()
        requests = get_requests()

        resp = requests.get(
            'https://api.bitbucket.org/2.0/repositories/%s/%s/src' % (
                parts['owner'],
                parts['code'],
            ),
            allow_redirects=False,
        )

        if not resp.ok:
            raise DoesNotExistError()
        base_url = resp.headers['Location']

        for filename in ('tidypy', 'pyproject.toml'):
            resp = requests.get('%s/%s' % (base_url, filename))

            if resp.ok:
                return cls.parse(
                    resp.text,
                    is_pyproject=filename == 'pyproject.toml',
                )

        raise DoesNotExistError()

