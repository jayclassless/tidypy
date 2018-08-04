from __future__ import absolute_import

import six

from .base import PythonTool, Issue, AccessIssue


class EradicateIssue(Issue):
    tool = 'eradicate'
    pylint_type = 'R'


CODE = 'commented'
DESCRIPTION = 'Commented-out code'


class EradicateTool(PythonTool):
    """
    Eradicate finds commented-out code in Python files.
    """

    @classmethod
    def can_be_used(cls):
        return not six.PY3

    @classmethod
    def get_all_codes(cls):
        return [(CODE, DESCRIPTION)]

    def execute(self, finder):  # pragma: PY2
        from eradicate import commented_out_code_line_numbers  # noqa: no-name-in-module

        issues = []
        if CODE in self.config['disabled']:
            return issues

        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath).decode('utf-8')
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

            for line in commented_out_code_line_numbers(source):
                issues.append(EradicateIssue(
                    CODE,
                    DESCRIPTION,
                    filepath,
                    line,
                ))

        return issues

