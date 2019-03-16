import os.path

from .base import Report


class PyLintReport(Report):
    """
    Generates a report that is in the same format as Pylint's default output.
    """

    TMPL_FILENAME = '************* Module {module}'
    TMPL_ISSUE = '{type}:{line:>3},{character:>2}: {message} ({code}@{tool})'

    def execute(self, collector):
        issues = collector.get_grouped_issues()

        for filename in sorted(issues.keys()):
            self.output(self.TMPL_FILENAME.format(
                module=self.make_module(filename),
            ))

            for issue in issues[filename]:
                self.output(self.TMPL_ISSUE.format(
                    file=self.relative_filename(filename),
                    line=issue.line,
                    character=(issue.character or 1) - 1,
                    tool=issue.tool,
                    code=issue.code,
                    message=issue.message,
                    type=issue.pylint_type
                ))

    def make_module(self, filename):
        filename = self.relative_filename(filename)
        root, ext = os.path.splitext(filename)
        if ext == '.py':
            return root.replace('/', '.')
        return filename


class PyLintParseableReport(PyLintReport):
    """
    Generates a report that is in roughly the same format as Pylint's
    "parseable" output.
    """

    TMPL_ISSUE = '{file}:{line}: [{tool}({code}), ] {message}'

