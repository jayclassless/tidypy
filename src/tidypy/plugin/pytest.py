
import pytest

from ..config import get_project_config
from ..core import execute_tools
from ..reports.console import ConsoleReport


def pytest_addoption(parser):
    group = parser.getgroup(
        'tidypy',
        'static analysis of a project with TidyPy',
    )

    group.addoption(
        '--tidypy',
        action='store_true',
        dest='tidypy',
        default=False,
        help='Enable the TidyPy plugin.'
    )

    group.addoption(
        '--tidypy-project-path',
        action='store',
        dest='tidypy_project_path',
        default=None,
        help='The path to the base of the project to analyze with TidyPy.'
    )

    group.addoption(
        '--tidypy-fail-on-issue',
        action='store_true',
        dest='tidypy_fail_on_issue',
        default=False,
        help='Whether or not pytest should fail if TidyPy finds issues.'
    )


def pytest_configure(config):
    if config.getoption('tidypy'):
        if not config.pluginmanager.hasplugin('_tidypy'):
            plugin = TidyPyPlugin(config)
            config.pluginmanager.register(plugin, '_tidypy')


class PyTestReport(ConsoleReport):
    def __init__(self, config, base_path, terminal_reporter):
        super().__init__(config, base_path)
        self.terminal_reporter = terminal_reporter

    def output(self, msg, newline=True):
        if newline:
            msg += '\n'
        self.terminal_reporter.write(msg)

    def execute(self, collector):
        self.output('TidyPy Results:\n')
        super().execute(collector)


class TidyPyPlugin(object):
    def __init__(self, config):
        self.enabled = config.getoption('tidypy')
        self.project_path = config.getoption('tidypy_project_path') \
            or str(config.rootdir)
        self.fail_on_issue = config.getoption('tidypy_fail_on_issue')
        self.tidypy_config = get_project_config(self.project_path)
        self._session_results = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtestloop(self, session):
        yield

        if self.enabled:
            self._session_results = execute_tools(
                self.tidypy_config,
                self.project_path,
            )

            if self.fail_on_issue and self._session_results.issue_count() > 0:
                session.testsfailed += 1

    def pytest_terminal_summary(self, terminalreporter):
        report = PyTestReport(
            self.tidypy_config,
            self.project_path,
            terminalreporter,
        )
        report.execute(self._session_results)

