from __future__ import absolute_import

import os.path

from pylint.lint import PyLinter
from pylint.reporters import BaseReporter

from ..util import mod_sys_path, compile_masks, matches_masks
from .base import Tool, Issue, AccessIssue, ParseIssue


class PyLintIssue(Issue):
    tool = 'pylint'


class TidyPyReporter(BaseReporter):
    name = 'tidypy'

    def __init__(self, message_store, filters):
        BaseReporter.__init__(self, output=None)
        self._message_store = message_store
        self._filters = compile_masks(filters)
        self._tidypy_issues = []

    def handle_message(self, msg):
        if self._filters and not matches_masks(msg.abspath, self._filters):
            return

        if msg.symbol == 'syntax-error':
            issue = ParseIssue(
                msg.msg,
                msg.abspath,
                line=msg.line,
                character=msg.column,
            )

        elif msg.symbol == 'parse-error':
            if 'Unable to load file' in msg.msg:
                issue = AccessIssue(
                    msg.msg.split('\n', 1)[1],
                    msg.abspath,
                )

            else:
                issue = ParseIssue(
                    msg.msg,
                    msg.abspath,
                    line=msg.line,
                    character=msg.column,
                )

        else:
            issue = PyLintIssue(
                code=msg.symbol or msg.msg_id,
                message=msg.msg,
                filename=msg.abspath,
                line=msg.line,
                character=msg.column,
            )

        self._tidypy_issues.append(issue)

    def _display(self, layout):
        pass

    def get_issues(self):
        return self._tidypy_issues


class PyLintTool(Tool):
    ALWAYS_DISABLED = [
        'locally-disabled',
        'locally-enabled',
        'suppressed-message',
    ]

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = []
        config['plugins'] = []
        return config

    @classmethod
    def get_all_codes(cls):
        pylint = PyLinter()
        pylint.load_default_plugins()

        codes = []
        for msg in pylint.msgs_store.messages:
            codes.append((
                msg.symbol or msg.msgid,
                msg.msg.replace('\n', ' '),
            ))

        return codes

    def execute(self, finder):
        packages = list(finder.packages(filters=self.config['filters']))
        modules = [
            mod
            for mod in finder.modules(filters=self.config['filters'])
            if os.path.dirname(mod) not in packages
        ]
        targets = modules + finder.topmost_directories(packages)
        if not targets:
            return []

        pylint = PyLinter()

        pylint.load_default_plugins()
        pylint.load_plugin_modules(self.config['plugins'])

        reporter = TidyPyReporter(
            pylint.msgs_store,
            filters=self.config['filters'],
        )
        pylint.set_reporter(reporter)

        for checker in pylint.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if option[0] in self.config['options']:
                    checker.set_option(
                        option[0],
                        self.config['options'][option[0]],
                    )

        for disabled in self.config['disabled'] + self.ALWAYS_DISABLED:
            pylint.disable(disabled)

        sys_paths = finder.sys_paths(filters=self.config['filters'])
        with mod_sys_path(sys_paths):
            pylint.check(targets)

        return reporter.get_issues()

