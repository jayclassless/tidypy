
import sys

from nose.plugins import Plugin

from ..config import get_project_config
from ..core import execute_tools
from ..reports.console import ConsoleReport


class TidyPy(Plugin):
    """Executes TidyPy on the project and shows the results."""

    name = 'tidypy'
    project_path = None
    fail_on_issue = False

    def options(self, parser, env):
        super().options(parser, env)

        parser.add_option(
            '--tidypy-project-path',
            action='store',
            dest='tidypy_project_path',
            default=env.get('TIDYPY_PROJECT_PATH', None),
            metavar='PATH',
            help='The path to the base of the project to analyze with TidyPy.'
            ' [TIDYPY_PROJECT_PATH]',
        )

        parser.add_option(
            '--tidypy-fail-on-issue',
            action='store_true',
            dest='tidypy_fail_on_issue',
            default=env.get('TIDYPY_FAIL_ON_ISSUE', False),
            help='Whether or not nose should fail if TidyPy finds issues.'
            ' [TIDYPY_FAIL_ON_ISSUE]',
        )

    def configure(self, options, conf):
        super().configure(options, conf)
        if not self.enabled:
            return
        self.project_path = options.tidypy_project_path or conf.workingDir
        self.fail_on_issue = options.tidypy_fail_on_issue

    def report(self, stream):
        cfg = get_project_config(self.project_path)
        collector = execute_tools(cfg, self.project_path)

        report = ConsoleReport(cfg, self.project_path, output_file=stream)
        report.execute(collector)

        if self.fail_on_issue and collector.issue_count() > 0:
            sys.exit(1)

