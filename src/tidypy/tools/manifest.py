
import os

from functools import partial

import check_manifest

from .base import Tool, Issue


IGNORE_MSGS = (
    'lists of files in version control and sdist match',
)


class CheckManifestIssue(Issue):
    tool = 'manifest'
    pylint_type = 'W'


class CheckManifestTool(Tool):
    """
    Uses the check-manifest script to detect discrepancies or problems with
    your project's MANIFEST.in file.
    """

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'setup\.py$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            ('info', 'info'),
            ('warning', 'warning'),
            ('error', 'error'),
        ]

    def execute(self, finder):
        issues = []

        def capture(code, message):
            if message in IGNORE_MSGS:
                return
            issues.append(CheckManifestIssue(
                code,
                message,
                os.path.join(dirname, 'MANIFEST.in'),
            ))

        check_manifest.info = partial(capture, 'info')
        check_manifest.warning = partial(capture, 'warning')
        check_manifest.error = partial(capture, 'error')

        for filepath in finder.files(self.config['filters']):
            dirname, _ = os.path.split(filepath)
            check_manifest.check_manifest(dirname)

        return issues

