
import sys

from threading import Lock, Timer

from tqdm import tqdm

from .config import get_tools


class Progress(object):
    """
    An interface for receiving events that occur during the execution of the
    TidyPy tool suite.
    """

    def __init__(self):
        self.current_tools = []
        self.completed_tools = []
        self._lock = Lock()

    def on_start(self):
        """
        Called when the execution of the TidyPy tool suite begins.
        """

    def on_tool_start(self, tool):
        """
        Called when an individual tool begins execution.

        :param tool: the name of the tool that is starting
        :type tool: str
        """

        with self._lock:
            self.current_tools.append(tool)

    def on_tool_finish(self, tool):
        """
        Called when an individual tool completes execution.

        :param tool: the name of the tool that completed
        :type tool: str
        """

        with self._lock:
            if tool in self.current_tools:
                self.current_tools.remove(tool)
                self.completed_tools.append(tool)

    def on_finish(self):
        """
        Called after all tools in the suite have completed.
        """


class QuietProgress(Progress):
    """
    An implementation of ``tidypy.Progress`` that produces no output.
    """


class ConsoleProgress(Progress):
    """
    An implementation of ``tidypy.Progress`` that outputs a progress bar to the
    console.
    """

    def __init__(self, config):
        super().__init__()
        self._timer = None

        tools = [
            name
            for name in get_tools()
            if config[name]['use']
        ]

        tqdm.monitor_interval = 0
        self._bar = tqdm(
            total=len(tools),
            desc='Analyzing',
            unit='tool',
            dynamic_ncols=True,
            bar_format='Analyzing |{bar}|'
            ' {percentage:3.0f}% [{elapsed}{postfix}]',
        )

    def _refresh(self):
        self._bar.refresh()
        self._timer = Timer(1.0, self._refresh)
        self._timer.start()

    @property
    def currently_executing(self):
        if not self.current_tools:
            return ''
        return '[%s]' % (
            ', '.join(self.current_tools),
        )

    def on_start(self):
        super().on_start()
        self._timer = Timer(1.0, self._refresh)
        self._timer.start()

    def on_tool_start(self, tool):
        super().on_tool_start(tool)
        self._bar.set_postfix({
            'current': ','.join(self.current_tools),
        })

    def on_tool_finish(self, tool):
        do_update = tool in self.current_tools
        super().on_tool_finish(tool)
        if do_update:
            postfix = {
                'current': ','.join(self.current_tools),
            }
            if not postfix['current']:
                del postfix['current']
            self._bar.set_postfix(postfix, refresh=False)
            self._bar.update()

    def on_finish(self):
        super().on_finish()
        print('', file=sys.stderr)
        self._timer.cancel()
        self._bar.close()

