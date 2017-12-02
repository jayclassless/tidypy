
import sys

from multiprocessing import Process
from multiprocessing.managers import SyncManager

from six import iteritems
from six.moves.queue import Empty  # pylint: disable=import-error

from .collector import Collector
from .config import get_tools, get_reports
from .finder import Finder
from .progress import QuietProgress
from .tools import ToolIssue
from .util import SysOutCapture


class Worker(Process):
    def notify(self, notification):
        self._args[1].put(notification)

    def start_tool(self):
        try:
            tool = self._args[0].get_nowait()
        except Empty:
            return None

        self.notify({
            'type': 'start',
            'tool': tool['name'],
        })

        return tool

    def complete_tool(self, tool, issues):
        self.notify({
            'type': 'complete',
            'tool': tool['name'],
            'issues': issues,
        })

    def run(self):
        finder = self._args[2]['finder']

        while True:
            tool = self.start_tool()
            if not tool:
                break

            issues = []
            try:
                with SysOutCapture() as capture:
                    impl = get_tools()[tool['name']](tool['config'])
                    issues = impl.execute(finder)

                    out = capture.get_stdout()
                    if out:  # pragma: no cover
                        issues.append(ToolIssue(
                            '%s: Extraneous output to stdout' % (
                                tool['name'],
                            ),
                            finder.project_path,
                            details=out,
                        ))
                    err = capture.get_stderr()
                    if err:  # pragma: no cover
                        issues.append(ToolIssue(
                            '%s: Extraneous output to stderr' % (
                                tool['name'],
                            ),
                            finder.project_path,
                            details=err,
                        ))
            except Exception:  # pragma: no cover  # noqa: broad-except
                issues = [ToolIssue(
                    '%s: Unexpected exception' % (tool['name'],),
                    finder.project_path,
                    details=sys.exc_info(),
                    failure=True,
                )]

            self.complete_tool(tool, issues)


def execute_tools(config, path, progress=None):
    progress = progress or QuietProgress()
    progress.on_start()

    manager = SyncManager()
    manager.start()

    num_tools = 0
    tools = manager.Queue()
    for name, cls in iteritems(get_tools()):
        if config[name]['use'] and cls.can_be_used():
            num_tools += 1
            tools.put({
                'name': name,
                'config': config[name],
            })

    collector = Collector(config)
    if not num_tools:
        progress.on_finish()
        return collector

    notifications = manager.Queue()
    environment = manager.dict({
        'finder': Finder(path, config),
    })

    workers = []
    for _ in range(config['workers']):
        worker = Worker(
            args=(
                tools,
                notifications,
                environment,
            ),
        )
        worker.start()
        workers.append(worker)

    while num_tools:
        try:
            notification = notifications.get(True, 0.25)
        except Empty:
            pass
        else:
            if notification['type'] == 'start':
                progress.on_tool_start(notification['tool'])
            elif notification['type'] == 'complete':
                collector.add_issues(notification['issues'])
                progress.on_tool_finish(notification['tool'])
                num_tools -= 1

    progress.on_finish()

    return collector


def execute_reports(
        config,
        path,
        collector,
        on_report_finish=None,
        output_file=None):
    reports = get_reports()
    for report in config['reports']:
        if report.get('type') and report['type'] in reports:
            reporter = reports[report['type']](
                report,
                path,
                output_file=output_file,
            )
            reporter.produce(collector)
            if on_report_finish:
                on_report_finish(report)

