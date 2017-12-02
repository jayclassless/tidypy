from __future__ import absolute_import

import sys

from threading import Lock, Timer

import six

from tqdm import tqdm

from .config import get_tools


class Progress(object):
    def __init__(self):
        self.current_tools = []
        self.completed_tools = []
        self._lock = Lock()

    def on_start(self):
        pass

    def on_tool_start(self, tool):
        with self._lock:
            self.current_tools.append(tool)

    def on_tool_finish(self, tool):
        with self._lock:
            if tool in self.current_tools:
                self.current_tools.remove(tool)
                self.completed_tools.append(tool)

    def on_finish(self):
        pass


class QuietProgress(Progress):
    pass


class ConsoleProgress(Progress):
    def __init__(self, config):
        super(ConsoleProgress, self).__init__()
        self._timer = None

        tools = [
            name
            for name in get_tools()
            if config[name]['use']
        ]

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
        super(ConsoleProgress, self).on_start()
        self._timer = Timer(1.0, self._refresh)
        self._timer.start()

    def on_tool_start(self, tool):
        super(ConsoleProgress, self).on_tool_start(tool)
        self._bar.set_postfix({
            'current': ','.join(self.current_tools),
        })

    def on_tool_finish(self, tool):
        do_update = tool in self.current_tools
        super(ConsoleProgress, self).on_tool_finish(tool)
        if do_update:
            postfix = {
                'current': ','.join(self.current_tools),
            }
            if not postfix['current']:
                del postfix['current']
            self._bar.set_postfix(postfix, refresh=False)
            self._bar.update()

    def on_finish(self):
        super(ConsoleProgress, self).on_finish()
        six.print_('', file=sys.stderr)
        self._timer.cancel()
        self._bar.close()

