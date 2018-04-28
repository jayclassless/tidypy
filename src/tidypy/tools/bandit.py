from __future__ import absolute_import

import re
import sys

from bandit import manager, config as bandit_config
from bandit.core import extension_loader
from six import iteritems, itervalues

from .base import PythonTool, Issue, ParseIssue, AccessIssue, UnknownIssue


class BanditIssue(Issue):
    tool = 'bandit'
    pylint_type = 'R'


SKIPPED_PARSE = re.compile(
    r'(exception while scanning file|syntax error while parsing AST from file)'
)

SKIPPED_ACCESS = re.compile(
    r'Permission denied'
)

RATING = {
    'LOW': 1,
    'MEDIUM': 2,
    'HIGH': 3,
}


class TidyPyBanditManager(manager.BanditManager):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.config = kwargs.pop('config')
        super(TidyPyBanditManager, self).__init__(
            bandit_config.BanditConfig(),
            'file',
            ignore_nosec=self.config['options']['ignore-nosec'],
            profile={
                'exclude': self.config['disabled'],
            },
        )
        self.progress = sys.maxsize  # prevent bandit from printing progress

    def discover_files(self, finder):  # pylint: disable=arguments-differ
        self.files_list = list(finder.files(self.config['filters']))
        self.skipped = []
        self.excluded_files = []

    def get_issues(self):
        issues = []

        for filepath, reason in self.skipped:
            if SKIPPED_PARSE.search(reason):
                issues.append(ParseIssue(reason, filepath))
            elif SKIPPED_ACCESS.search(reason):
                issues.append(AccessIssue(reason, filepath))
            else:
                issues.append(UnknownIssue(reason, filepath))

        min_severity = RATING[self.config['options']['severity'].upper()]
        min_confidence = RATING[self.config['options']['confidence'].upper()]
        for issue in self.get_issue_list():
            if RATING[issue.severity] < min_severity \
                    or RATING[issue.confidence] < min_confidence:
                continue

            issues.append(BanditIssue(
                issue.test_id,
                issue.text,
                issue.fname,
                issue.lineno,
            ))

        return issues


class BanditTool(PythonTool):
    """
    Bandit is a security linter for Python source code.
    """

    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options']['confidence'] = 'low'
        config['options']['severity'] = 'low'
        config['options']['ignore-nosec'] = False
        return config

    @classmethod
    def get_all_codes(cls):
        codes = [
            (code, plugin.name)
            for code, plugin in iteritems(
                extension_loader.MANAGER.plugins_by_id
            )
        ]

        codes += [
            (blacklist['id'], blacklist['message'])
            for blacklist in itervalues(
                extension_loader.MANAGER.blacklist_by_id
            )
        ]

        return codes

    def __init__(self, *args, **kwargs):
        super(BanditTool, self).__init__(*args, **kwargs)
        self.bandit = TidyPyBanditManager(config=self.config)

    def execute(self, finder):
        self.bandit.discover_files(finder)
        self.bandit.run_tests()
        return self.bandit.get_issues()

