
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^bitbucket-snippet:(?P<owner>[^/]+)/(?P<code>.+)$')


class BitbucketSnippetExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    Bitbucket Snippets.
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
                'https://bitbucket.org/api/2.0/snippets/%s/%s/files/%s' % (
                    parts['owner'],
                    parts['code'],
                    filename
                ),
            )

            if resp.ok:
                return cls.parse(
                    resp.text,
                    is_pyproject=filename == 'pyproject.toml',
                )

        raise DoesNotExistError()

