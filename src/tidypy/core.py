
import sys

from threading import Thread

from six import iteritems
from six.moves.queue import Queue  # pylint: disable=import-error

from .collector import Collector
from .config import get_tools, get_reports
from .finder import Finder
from .tools import ToolIssue
from .util import SysOutCapture


def execute_tools(config, path, on_tool_start=None, on_tool_finish=None):
    finder = Finder(path, config)
    collector = Collector(config)
    tool_queue = Queue()

    for name, cls in iteritems(get_tools()):
        if config[name]['use'] and cls.can_be_used():
            tool_queue.put(name)

    def worker():
        while True:
            tool_name = tool_queue.get()
            if on_tool_start:
                on_tool_start(tool_name)

            try:
                tool = get_tools()[tool_name](config[tool_name])
                collector.add_issues(tool.execute(finder))
            except Exception:  # pylint: disable=broad-except
                collector.add_issues(ToolIssue(
                    '%s failed horribly' % (tool_name,),
                    path,
                    details=sys.exc_info(),
                    failure=True,
                ))

            if on_tool_finish:
                on_tool_finish(tool_name)
            tool_queue.task_done()

    with SysOutCapture() as capture:
        for _ in range(config['threads']):
            thread = Thread(target=worker)
            thread.daemon = True
            thread.start()

        tool_queue.join()

        out = capture.get_stdout()
        if out:
            collector.add_issues(ToolIssue(
                'Tool(s) wrote to stdout',
                path,
                details=out,
            ))
        err = capture.get_stderr()
        if err:
            collector.add_issues(ToolIssue(
                'Tool(s) wrote to stderr',
                path,
                details=err,
            ))

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

