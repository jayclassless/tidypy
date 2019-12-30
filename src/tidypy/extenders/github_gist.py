
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^github-gist:([^/]+/)?(?P<code>.+)$')


class GithubGistExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    GitHub Gists.
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
            'https://api.github.com/gists/%s' % (
                parts['code'],
            ),
        )

        files = [
            gfile
            for gfile in resp.json().get('files', {}).values()
            if gfile['filename'] in ('tidypy', 'pyproject.toml')
        ]

        if not files:
            raise DoesNotExistError()

        return cls.parse(
            files[0]['content'],
            is_pyproject=files[0]['filename'] == 'pyproject.toml',
        )

