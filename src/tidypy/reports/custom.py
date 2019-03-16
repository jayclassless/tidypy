from .base import Report

from ..util import output_error


class CustomReport(Report):
    """
    Prints output to the console according to a user-defined template.
    """

    def execute(self, collector):
        template = self.config.get(
            'format',
            '{filename}:{line}:{character}:{tool}:{code}:{message}',
        )
        try:
            template.format(
                filename='',
                full_filename='',
                line=1,
                character=1,
                code='',
                tool='',
                message='',
            )
        except Exception as exc:  # noqa: broad-except
            if isinstance(exc, KeyError):
                error = 'Unknown token {}'.format(exc)
            else:
                error = exc
            output_error('Invalid format for custom report: {}'.format(error))
            return

        issues = collector.get_issues(sortby=('filename', 'line', 'character'))
        for issue in issues:
            self.output(
                template.format(
                    filename=self.relative_filename(issue.filename),
                    full_filename=issue.filename,
                    line=issue.line,
                    character=issue.character or 0,
                    code=issue.code,
                    tool=issue.tool,
                    message=issue.message,
                )
            )

