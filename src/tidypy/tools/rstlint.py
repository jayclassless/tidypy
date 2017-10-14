
from docutils.nodes import system_message
from docutils.utils import Reporter
from restructuredtext_lint import lint

from .base import Tool, Issue, AccessIssue, UnknownIssue


class RstLintIssue(Issue):
    tool = 'rstlint'

    @property
    def pylint_type(self):
        if self.code in ('error', 'severe'):
            return 'E'
        return 'W'


class RstLintTool(Tool):
    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.rst$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (level.lower(), level)
            for level in Reporter.levels
        ]

    def execute(self, finder):
        issues = []

        for filepath in finder.files(self.config['filters']):
            try:
                errors = lint(
                    finder.read_file(filepath),
                    filepath=filepath,
                )
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
            else:
                issues += [
                    self.make_issue(error, filepath)
                    for error in errors
                ]

        return [
            issue
            for issue in issues
            if issue.code not in self.config['disabled']
        ]

    def make_issue(self, error, filename):
        if isinstance(error, system_message):
            return RstLintIssue(
                error.type.lower(),
                error.message,
                filename,
                error.line,
            )

        if isinstance(error, EnvironmentError):
            return AccessIssue(error, filename)

        return UnknownIssue(error, filename)

