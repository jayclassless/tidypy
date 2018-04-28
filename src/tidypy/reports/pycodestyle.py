from .base import Report


class PyCodeStyleReport(Report):
    """
    Generates a report that is in the same format as pycodestyle's default
    output.
    """

    def execute(self, collector):
        issues = collector.get_issues(sortby=('filename', 'line', 'character'))
        for issue in issues:
            self.output(
                '{filename}:{line}:{character} {code}@{tool} {message}'.format(
                    filename=self.relative_filename(issue.filename),
                    line=issue.line,
                    character=issue.character or 0,
                    code=issue.code,
                    tool=issue.tool,
                    message=issue.message,
                )
            )

