import sys

import click

from .base import Report


TMPL_FILENAME = click.style('{filename}', underline=True) + ' ({num_errors})'

TMPL_LOCATION = click.style(
    '{line:>5}{position_splitter}{character:<3} ',
    dim=True,
)

TMPL_TOOLINFO = click.style('({tool}:{code})', fg='yellow', dim=True)

TAB = ' ' * 8


class ConsoleReport(Report):
    """
    Prints a colored report to the console that groups issues by the file they
    were found in.
    """

    def execute(self, collector):
        issues = collector.get_grouped_issues()

        total_issues = 0
        for filename in sorted(issues.keys()):
            file_issues = issues[filename]
            total_issues += len(file_issues)

            self.output(TMPL_FILENAME.format(
                filename=self.relative_filename(filename),
                num_errors=len(file_issues),
            ))

            for issue in file_issues:
                location = TMPL_LOCATION.format(
                    line=issue.line,
                    position_splitter=' ' if issue.character is None else ':',
                    character=issue.character or '',
                )

                toolinfo = TMPL_TOOLINFO.format(
                    tool=issue.tool,
                    code=issue.code,
                )

                message = issue.message
                if '\n' in message:
                    pad = '\n' + (' ' * len(click.unstyle(location)))

                    message = pad.join(
                        issue.message.replace('\t', TAB).splitlines()
                    )

                    toolinfo = pad + toolinfo
                else:
                    toolinfo = ' ' + toolinfo

                self.output(location + message + toolinfo)

            self.output('')

        is_windows = sys.platform == 'win32'
        if total_issues:
            self.output(
                click.style(
                    u'{icon}{num_issues} issues found.'.format(  # noqa: @2to3
                        icon='' if is_windows else u'\u2717 ',  # noqa: @2to3
                        num_issues=total_issues,
                    ),
                    fg='yellow',
                    bold=True,
                )
            )
        else:
            self.output(
                click.style(
                    u'{icon}No issues found!'.format(  # noqa: @2to3
                        icon='' if is_windows else u'\u2714 ',  # noqa: @2to3
                    ),
                    fg='green',
                    bold=True,
                )
            )

