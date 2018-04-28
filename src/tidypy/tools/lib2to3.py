
from __future__ import absolute_import

import difflib
import re

from lib2to3.pgen2.parse import ParseError
from lib2to3.pgen2.tokenize import TokenError
from lib2to3.refactor import RefactoringTool, get_all_fix_names

from six import text_type, PY2

from .base import PythonTool, Issue, ParseIssue, AccessIssue, UnknownIssue


RE_UDIFF_LINE = re.compile(
    r'^@@ [-+](?P<line>\d+)(,\d+)? [-+](\d+)(,\d+)? @@$'
)

FIXER_PKG = 'lib2to3.fixes'


class TidyPyRefactoringTool(RefactoringTool):  # pragma: PY2
    def __init__(self, fixers):
        fixers = [
            '%s.fix_%s' % (FIXER_PKG, fixer)
            for fixer in fixers
        ]
        super(TidyPyRefactoringTool, self).__init__(fixers, explicit=fixers)
        self._tidypy_issues = []

    def get_diff(self, old, new):
        old = old.splitlines()
        new = new.splitlines()
        return list(difflib.unified_diff(old, new, n=0, lineterm=""))[2:]

    def print_output(self, old_text, new_text, filename, equal):
        if equal:
            return

        diff = self.get_diff(old_text, new_text)

        line_num = None
        batch = []
        for line in diff:
            match = RE_UDIFF_LINE.match(line)
            if match:
                if batch:
                    self.add_issue(filename, line_num, batch)
                line_num = match.groupdict()['line']
                batch = []
            else:
                batch.append(line)
        if batch:
            self.add_issue(filename, line_num, batch)

    def log_error(self, msg, *args, **kwds):
        if msg.startswith('Can\'t parse docstring'):
            self._tidypy_issues.append(ParseIssue(args[3], args[0]))

        elif msg.startswith('Can\'t parse'):
            line = None
            character = None

            if isinstance(args[2], TokenError):
                msg = args[2].args[0]
                line = args[2].args[1][0] - 1
                character = args[2].args[1][1] + 1
            elif isinstance(args[2], ParseError):
                msg = args[2].msg
            else:
                msg = text_type(args[2])

            self._tidypy_issues.append(ParseIssue(
                msg,
                args[0],
                line=line,
                character=character,
            ))

        elif isinstance(args[1], EnvironmentError):
            self._tidypy_issues.append(AccessIssue(args[1], args[0]))

        else:
            self._tidypy_issues.append(UnknownIssue(msg % args, args[0]))

    def log_message(self, msg, *args):
        pass

    def log_debug(self, msg, *args):
        pass

    def write_file(self, new_text, filename, old_text, encoding=None):
        pass

    def add_issue(self, filename, line, diff):
        message = 'Suggested change for Python 3 compatibility:\n%s' % (
            '\n'.join(diff),
        )
        self._tidypy_issues.append(Lib2to3Issue(
            code='change',
            message=message,
            filename=filename,
            line=int(line),
        ))

    def get_issues(self):
        return self._tidypy_issues


class Lib2to3Issue(Issue):
    tool = '2to3'
    pylint_type = 'E'


class Lib2to3Tool(PythonTool):
    """
    Uses Python's lib2to3 module to find code that should be changed in order
    to be compatible with Python 3.
    """

    @classmethod
    def get_default_config(cls):
        cfg = PythonTool.get_default_config()
        cfg['use'] = PY2
        return cfg

    @classmethod
    def get_all_codes(cls):
        return [
            (fixer, fixer)
            for fixer in get_all_fix_names(FIXER_PKG)
        ]

    def execute(self, finder):  # pragma: PY2
        fixers = get_all_fix_names(FIXER_PKG)
        for disabled in self.config['disabled']:
            if disabled in fixers:
                fixers.remove(disabled)

        tool = TidyPyRefactoringTool(fixers)

        for filepath in finder.files(self.config['filters']):
            tool.refactor([filepath])

        return tool.get_issues()

