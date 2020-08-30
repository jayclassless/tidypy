
from pep8ext_naming import NamingChecker
from pycodestyle import StyleGuide, BaseReport, register_check

from .base import PythonTool, Issue, AccessIssue, ParseIssue


class PyCodeStyleIssue(Issue):
    tool = 'pycodestyle'
    pylint_type = 'C'

    def __init__(self, code, message, filename, line, character):
        if code in ('E101',):
            line = None
        super().__init__(
            code,
            message,
            filename,
            line,
            character,
        )


class TidyPyReport(BaseReport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tidypy_issues = []

    def error(self, line_number, offset, text, check):
        code = super().error(
            line_number,
            offset,
            text,
            check,
        )

        if code == 'E901':
            message = text[5:].split(':', 1)[1].lstrip()
            self._tidypy_issues.append(ParseIssue(
                message,
                self.filename,
                line=line_number,
                character=offset + 1,
            ))

        elif code == 'E902':
            message = text[5:].split(':', 1)[1].lstrip()
            self._tidypy_issues.append(AccessIssue(message, self.filename))
        elif code:
            self._tidypy_issues.append(PyCodeStyleIssue(
                code,
                text[5:],
                self.filename,
                line_number,
                offset + 1,
            ))

        return code

    def get_issues(self):
        return self._tidypy_issues


class TidyPyStyleGuide(StyleGuide):
    def __init__(self, config):
        kwargs = {
            'reporter': TidyPyReport,
            'ignore': config['disabled'],
        }
        super().__init__(**kwargs)
        self.options.max_line_length = config['options']['max-line-length']
        self.options.hang_closing = config['options']['hang-closing']


class PyCodeStyleTool(PythonTool):
    """
    pycodestyle is a tool to check your Python code against some of the style
    conventions in PEP 8.
    """

    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options'] = {
            'max-line-length': 79,
            'hang-closing': False,
        }
        return config

    @classmethod
    def get_all_codes(cls):
        # pycodestyle doesn't have a way to introspect this.
        return ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checker = TidyPyStyleGuide(self.config)

    def execute(self, finder):
        report = self.checker.check_files(
            finder.files(self.config['filters']),
        )
        return report.get_issues()


register_check(NamingChecker)

