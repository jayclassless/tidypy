
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^gitlab:(?P<owner>[^/]+)/(?P<project>.+)$')


class GitlabExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    GitLab repositories.
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
            resp = get_requests().get(
                'https://gitlab.com/%s/%s/raw/master/%s' % (
                    parts['owner'],
                    parts['project'],
                    filename,
                ),
                allow_redirects=False,
            )

            if resp.status_code > 200:
                continue

            return cls.parse(
                resp.text,
                is_pyproject=filename == 'pyproject.toml',
            )

        raise DoesNotExistError()

