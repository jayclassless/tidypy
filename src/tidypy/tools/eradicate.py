
from eradicate import Eradicator

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
    def get_all_codes(cls):
        return [(CODE, DESCRIPTION)]

    def execute(self, finder):

        issues = []
        if CODE in self.config['disabled']:
            return issues

        eradicator = Eradicator()

        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath)
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

            for line in eradicator.commented_out_code_line_numbers(source):
                issues.append(EradicateIssue(
                    CODE,
                    DESCRIPTION,
                    filepath,
                    line,
                ))

        return issues

