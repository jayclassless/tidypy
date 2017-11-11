from __future__ import absolute_import

from threading import Lock

import six

from progress.bar import Bar

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

    def notify(self, message):
        pass


class QuietProgress(Progress):
    pass


class ConsoleProgress(Bar, Progress):
    suffix = '%(percent)d%% %(currently_executing)s %(notification)s'

    def __init__(self, config):
        Progress.__init__(self)

        self._notification = None

        tools = [
            name
            for name in get_tools()
            if config[name]['use']
        ]

        super(ConsoleProgress, self).__init__(
            'Analyzing:',
            max=len(tools),
        )
        self.update()

    @property
    def currently_executing(self):
        if not self.current_tools:
            return ''
        return '[%s]' % (
            ', '.join(self.current_tools),
        )

    @property
    def notification(self):
        if not self._notification:
            return ''
        return '[%s]' % (self._notification,)

    def notify(self, message):
        self._notification = message
        self.update()

    def on_tool_start(self, tool):
        super(ConsoleProgress, self).on_tool_start(tool)
        self.update()

    def on_tool_finish(self, tool):
        if tool in self.current_tools:
            self.next()  # noqa: @2to3
        super(ConsoleProgress, self).on_tool_finish(tool)

    def on_finish(self):
        super(ConsoleProgress, self).finish()
        six.print_('', file=self.file)
        self.file.flush()

