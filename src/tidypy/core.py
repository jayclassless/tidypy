
import sys

from concurrent.futures import ThreadPoolExecutor, as_completed
from six import iteritems

from .collector import Collector
from .config import get_tools, get_reports
from .finder import Finder
from .progress import QuietProgress
from .tools import ToolIssue
from .util import SysOutCapture


def _execute_tool(tool, finder, collector, progress):
    name, tool = tool
    progress.on_tool_start(name)

    try:
        collector.add_issues(tool.execute(finder))
    except Exception:  # pragma: no cover  # pylint: disable=broad-except
        collector.add_issues(ToolIssue(
            '%s failed horribly' % (name,),
            finder.project_path,
            details=sys.exc_info(),
            failure=True,
        ))

    progress.on_tool_finish(name)


def execute_tools(config, path, progress=None):
    progress = progress or QuietProgress()
    progress.on_start()

    collector = Collector(config)

    tools = [
        (name, cls(config[name]))
        for name, cls in iteritems(get_tools())
        if config[name]['use'] and cls.can_be_used()
    ]
    if not tools:
        return collector

    finder = Finder(path, config)

    with SysOutCapture() as capture:
        with ThreadPoolExecutor(max_workers=config['threads']) as executor:
            jobs = [
                executor.submit(
                    _execute_tool,
                    tool,
                    finder,
                    collector,
                    progress,
                )
                for tool in tools
            ]

            try:
                for future in as_completed(jobs):
                    future.result()
            except KeyboardInterrupt:  # pragma: no cover
                progress.notify('Stopping... please wait')
                collector.failure = True
                for job in jobs:
                    job.cancel()

        out = capture.get_stdout()
        if out:  # pragma: no cover
            collector.add_issues(ToolIssue(
                'Tool(s) wrote to stdout',
                path,
                details=out,
            ))
        err = capture.get_stderr()
        if err:  # pragma: no cover
            collector.add_issues(ToolIssue(
                'Tool(s) wrote to stderr',
                path,
                details=err,
            ))

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

