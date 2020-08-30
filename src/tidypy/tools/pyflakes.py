
import inspect

from pyflakes import messages
from pyflakes.api import check
from pyflakes.reporter import Reporter

from .base import PythonTool, Issue, AccessIssue, ParseIssue


class PyFlakesIssue(Issue):
    tool = 'pyflakes'


class TidyPyReporter(Reporter):
    def __init__(self, config):
        super().__init__(None, None)
        self._tidypy_issues = []
        self._config = config

    def unexpectedError(self, filename, msg):  # noqa
        if msg == 'problem decoding source':
            issue = ParseIssue
        else:
            issue = AccessIssue
        self._tidypy_issues.append(issue(
            msg,
            filename,
        ))

    def syntaxError(self, filename, msg, lineno, offset, text):  # noqa
        self._tidypy_issues.append(ParseIssue(
            msg,
            filename,
            line=lineno,
            character=offset,
        ))

    def flake(self, message):
        if message.__class__.__name__ in self._config['disabled']:
            return

        self._tidypy_issues.append(PyFlakesIssue(
            message.__class__.__name__,
            message.message % message.message_args,
            message.filename,
            message.lineno,
            message.col + 1,
        ))

    def get_issues(self):
        return self._tidypy_issues


class PyFlakesTool(PythonTool):
    """
    Pyflakes is a simple program which checks Python source files for errors.
    """

    @classmethod
    def get_all_codes(cls):
        codes = []

        for name in dir(messages):
            obj = getattr(messages, name)
            if inspect.isclass(obj) \
                    and obj is not messages.Message \
                    and issubclass(obj, messages.Message):
                codes.append((name, obj.message))

        return codes

    def execute(self, finder):
        issues = []
        reporter = TidyPyReporter(self.config)
        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath)
            except EnvironmentError as exc:
                issues.append(
                    AccessIssue(exc, filepath)
                )
            else:
                check(source, filepath, reporter)
        return reporter.get_issues() + issues

