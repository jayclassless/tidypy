
import logging

from pydocstyle import check, Error
from pydocstyle.parser import ParseError, AllError
from pydocstyle.violations import ErrorRegistry

from .base import PythonTool, Issue, AccessIssue, ParseIssue, UnknownIssue


class PyDocStyleIssue(Issue):
    tool = 'pydocstyle'
    pylint_type = 'C'


class PyDocStyleTool(PythonTool):
    """
    pydocstyle is a static analysis tool for checking compliance with Python
    docstring conventions (e.g., PEP 257).
    """

    @classmethod
    def get_all_codes(cls):
        return [
            (error.code, error.short_desc)
            for group in ErrorRegistry.groups
            for error in group.errors
        ]

    def execute(self, finder):
        issues = []

        logging.disable(logging.CRITICAL)

        for filepath in finder.files(self.config['filters']):
            issues += [
                self.make_issue(error, filepath)
                for error in check(
                    (filepath,),
                    ignore=self.config['disabled'],
                )
            ]

        logging.disable(logging.NOTSET)

        return issues

    def make_issue(self, error, filename):
        if isinstance(error, Error):
            return PyDocStyleIssue(
                error.code,
                error.short_desc,
                filename,
                error.line,
            )

        if isinstance(error, EnvironmentError):
            return AccessIssue(error, filename)

        if isinstance(error, (AllError, ParseError, SyntaxError)):
            return ParseIssue(error, filename)

        return UnknownIssue(error, filename)

