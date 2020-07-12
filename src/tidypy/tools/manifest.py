
import os

import check_manifest

from .base import Tool, Issue


IGNORE_MSGS = (
    'lists of files in version control and sdist match',
)


class CheckManifestIssue(Issue):
    tool = 'manifest'
    pylint_type = 'W'


class CheckManifestUI(check_manifest.UI):
    def __init__(self, dirname):
        super().__init__()
        self.dirname = dirname
        self.issues = []

    def _save_issue(self, code, message):
        if message in IGNORE_MSGS:
            return
        self.issues.append(CheckManifestIssue(
            code,
            message,
            os.path.join(self.dirname, 'MANIFEST.in'),
        ))

    def info(self, message):
        self._save_issue('info', message)

    def warning(self, message):
        self._save_issue('warning', message)

    def error(self, message):
        self._save_issue('error', message)


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

        for filepath in finder.files(self.config['filters']):
            dirname, _ = os.path.split(filepath)
            try:
                cmui = CheckManifestUI(dirname)
                check_manifest.check_manifest(dirname, ui=cmui)
            except check_manifest.Failure as exc:
                issues.append(CheckManifestIssue(
                    'error',
                    'Unexpected error: %s' % (exc,),
                    filepath,
                ))
            else:
                issues += cmui.issues

        return issues

