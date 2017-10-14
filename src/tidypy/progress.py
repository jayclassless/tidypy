from __future__ import absolute_import

from threading import Lock

import six

from progress.bar import Bar

from .config import get_tools


class TidyBar(Bar):
    suffix = '%(percent)d%% %(currently_executing)s'

    def __init__(self, config, quiet=False):
        self.quiet = quiet
        if self.quiet:
            return

        self._lock = Lock()

        tools = [
            name
            for name in get_tools()
            if config[name]['use']
        ]

        super(TidyBar, self).__init__(
            'Analyzing:',
            max=len(tools),
        )
        self._currently_executing = []
        self.update()

    @property
    def currently_executing(self):
        if not self._currently_executing:
            return ''
        return '[%s]' % (
            ', '.join(self._currently_executing),
        )

    def on_tool_start(self, tool):
        with self._lock:
            self._currently_executing.append(tool)
            self.update()

    def on_tool_finish(self, tool):
        with self._lock:
            if tool in self._currently_executing:
                self._currently_executing.remove(tool)
            if not self.quiet:
                self.next()

    def finish(self):
        if not self.quiet:
            super(TidyBar, self).finish()
            six.print_('', file=self.file)
            self.file.flush()

