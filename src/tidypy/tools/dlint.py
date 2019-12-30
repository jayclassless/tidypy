
from dlint import linters

from .base import PythonTool, Issue, AccessIssue, ParseIssue
from ..util import parse_python_file


class DlintIssue(Issue):
    tool = 'dlint'
    pylint_type = 'W'


# pylint: disable=protected-access


def get_linter_msg(linter, msg=None):
    msg = msg or linter._error_tmpl
    if msg.startswith(linter._code):
        return msg[len(linter._code) + 1:]
    return msg


class DlintTool(PythonTool):
    """
    Dlint is a tool for encouraging best coding practices and helping ensure
    we're writing secure Python code.
    """

    @classmethod
    def get_all_codes(cls):
        return [
            (linter._code, get_linter_msg(linter))
            for linter in linters.ALL
        ]

    def execute(self, finder):
        issues = []

        dlinters = [
            linter
            for linter in linters.ALL
            if linter._code not in self.config['disabled']
        ]

        for filepath in finder.files(self.config['filters']):
            try:
                tree = parse_python_file(filepath)
            except (SyntaxError, TypeError) as exc:
                issues.append(ParseIssue(exc, filepath))
                continue
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

            for linter in dlinters:
                linter_instance = linter()
                linter_instance.visit(tree)

                for result in linter_instance.get_results():
                    issues.append(DlintIssue(
                        code=linter._code,
                        message=get_linter_msg(linter, result.message),
                        filename=filepath,
                        line=result.lineno,
                        character=result.col_offset + 1,
                    ))

        return issues

