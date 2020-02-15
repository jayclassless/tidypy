
import base64
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^github:(?P<owner>[^/]+)/(?P<project>.+)$')


class GithubExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    GitHub repositories.
    """

    @classmethod
    def can_handle(cls, location):
        if RE_LOCATION.match(location):
            return True
        return False

    @classmethod
    def retrieve(cls, location, project_path):
        parts = RE_LOCATION.match(location).groupdict()

        for filename in ('tidypy', 'pyproject.toml'):
            content = cls.get_file(parts['owner'], parts['project'], filename)
            if content:
                return cls.parse(
                    content,
                    is_pyproject=filename == 'pyproject.toml',
                )

        raise DoesNotExistError()

    @classmethod
    def get_file(cls, owner, project, filename):
        resp = get_requests().get(
            'https://api.github.com/repos/%s/%s/contents/%s' % (
                owner,
                project,
                filename,
            ),
        ).json()

        if resp.get('type') == 'file' and resp.get('content'):
            return base64.b64decode(resp['content']).decode('utf-8')

        return None

