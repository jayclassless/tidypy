
import os

from pbbt import Test, Field, BaseCase, maybe

from ..config import get_project_config
from ..core import execute_tools
from ..reports.console import ConsoleReport


class PbbtReport(ConsoleReport):
    def __init__(self, config, base_path, pbbt_ui):
        super().__init__(config, base_path)
        self.pbbt_ui = pbbt_ui

    def output(self, msg, newline=True):
        self.pbbt_ui.literal(msg or ' ')


@Test
class TidyPyCase(BaseCase):
    class Input(object):  # noqa: pydocstyle:D106
        tidypy = Field(
            maybe(str),
            hint='The path to the base of project. Defaults to CWD.',
        )

        fail_on_issue = Field(
            bool,
            default=True,
            hint='Whether or not the test should fail if TidyPy finds issues.'
        )

    def check(self):
        project_path = self.input.tidypy or os.getcwd()

        cfg = get_project_config(project_path)
        collector = execute_tools(cfg, project_path)

        report = PbbtReport(cfg, project_path, self.ui)
        report.execute(collector)

        if self.input.fail_on_issue and collector.issue_count() > 0:
            self.ctl.failed('Issues found.')

