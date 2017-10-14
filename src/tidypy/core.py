
import traceback

from threading import Thread

from six.moves.queue import Queue  # pylint: disable=import-error

from .collector import Collector
from .config import get_tools, get_reports
from .finder import Finder
from .util import output_error


def execute_tools(config, path, on_tool_start=None, on_tool_finish=None):
    finder = Finder(path, config)
    collector = Collector(config)
    tool_queue = Queue()

    for name in get_tools():
        if config[name]['use']:
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
                if not config['silence_tool_crashes']:
                    output_error(
                        'The "%s" tool failed horribly:' % (
                            tool_name,
                        ),
                    )
                    output_error(traceback.format_exc())
            finally:
                if on_tool_finish:
                    on_tool_finish(tool_name)
                tool_queue.task_done()

    for _ in range(config['threads']):
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

    tool_queue.join()

    return collector


def execute_reports(config, path, collector, on_report_finish=None):
    reports = get_reports()
    for report in config['reports']:
        if report.get('type') and report['type'] in reports:
            reporter = reports[report['type']](report, path)
            reporter.execute(collector)
            if on_report_finish:
                on_report_finish(report)

