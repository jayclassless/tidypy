
import cgi
import re

from ..util import get_requests
from .base import Extender, DoesNotExistError


RE_LOCATION = re.compile(r'^gitlab-snippet:(?P<code>.+)$')


class GitlabSnippetExtender(Extender):
    """
    Retrieves configurations from pyproject.toml or tidypy files in public
    GitLab Snippets.
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
            'https://gitlab.com/snippets/%s/raw' % (parts['code'],),
            allow_redirects=False,
        )

        if resp.status_code > 200:
            raise DoesNotExistError()

        filename = resp.headers.get('Content-Disposition', None)
        if filename:
            _, opts = cgi.parse_header(filename)
            filename = opts.get('filename', None)

        return cls.parse(resp.text, is_pyproject=filename == 'pyproject.toml')

