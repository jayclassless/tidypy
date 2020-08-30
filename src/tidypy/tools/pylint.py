
import os.path

from pathlib import Path

import astroid

from pylint.exceptions import UnknownMessageError
from pylint.lint import PyLinter
from pylint.reporters import BaseReporter

from ..util import mod_sys_path, compile_masks, matches_masks
from .base import Tool, Issue, AccessIssue, ParseIssue


class PyLintIssue(Issue):
    tool = 'pylint'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.character is not None:
            self.character += 1


class TidyPyReporter(BaseReporter):
    name = 'tidypy'

    def __init__(self, message_store, filters, finder, targets):
        BaseReporter.__init__(self, output=None)
        self._message_store = message_store
        self._filters = compile_masks(filters)
        self._targets = targets
        self._finder = finder
        self._all_files = list(finder.files(filters=filters))
        self._tidypy_issues = []

    def _resolve_filename(self, modname):
        name = modname.replace('.', os.sep) + '.py'

        for target in self._targets:
            resolved = str(Path(target).parent / name)
            if resolved in self._all_files:
                return resolved

        return None

    def _is_excluded(self, path):
        return self._finder.is_excluded(Path(path)) \
            or (self._filters and not matches_masks(path, self._filters))

    def _handle_duplicate_code(self, msg):
        issues = []

        pylint_msg = msg.msg.splitlines()

        dupe_files = []
        for line in pylint_msg[1:]:
            if line.startswith('=='):
                name, line = line[2:].rsplit(':', 1)
                name = self._resolve_filename(name)
                if name:
                    dupe_files.append((
                        name,
                        int(line) + 1,
                    ))
            else:
                break

        num_lines = len(pylint_msg) - len(dupe_files)

        if len(dupe_files) > 1:
            for dupe_file in dupe_files:
                other_files = [
                    '%s:%s' % (
                        self._finder.relative_to_project(dfile[0]),
                        dfile[1],
                    )
                    for dfile in dupe_files
                    if dfile[0] != dupe_file[0]
                ]
                issues.append(PyLintIssue(
                    code=msg.symbol,
                    message='Found %s similar lines other files:\n%s' % (
                        num_lines,
                        '\n'.join(other_files),
                    ),
                    filename=dupe_file[0],
                    line=dupe_file[1],
                ))

        return issues

    def handle_message(self, msg):
        issues = []
        is_excluded = self._is_excluded(msg.abspath)

        if not is_excluded and msg.symbol == 'syntax-error':
            issues.append(ParseIssue(
                msg.msg,
                msg.abspath,
                line=msg.line,
                character=msg.column,
            ))

        elif not is_excluded and msg.symbol == 'parse-error':
            if 'Unable to load file' in msg.msg:
                issues.append(AccessIssue(
                    msg.msg.split('\n', 1)[1],
                    msg.abspath,
                ))

            else:
                issues.append(ParseIssue(
                    msg.msg,
                    msg.abspath,
                    line=msg.line,
                    character=msg.column,
                ))

        elif msg.symbol == 'duplicate-code':
            issues.extend(self._handle_duplicate_code(msg))

        elif not is_excluded:
            issues.append(PyLintIssue(
                code=msg.symbol or msg.msg_id,
                message=msg.msg,
                filename=msg.abspath,
                line=msg.line,
                character=msg.column,
            ))

        self._tidypy_issues.extend(issues)

    def _display(self, layout):
        pass

    def get_issues(self):
        return self._tidypy_issues


class PyLintTool(Tool):
    """
    Pylint is a Python source code analyzer which looks for programming errors,
    helps enforcing a coding standard and sniffs for some code smells.
    """

    ALWAYS_DISABLED = [
        'locally-disabled',
        'locally-enabled',
        'suppressed-message',
    ]

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = []
        config['options']['plugins'] = []
        config['options']['extension-pkg-whitelist'] = []
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
        pylint.load_plugin_modules(self.config['options']['plugins'])
        astroid.MANAGER.extension_package_whitelist.update(
            self.config['options']['extension-pkg-whitelist'],
        )

        reporter = TidyPyReporter(
            pylint.msgs_store,
            filters=self.config['filters'],
            finder=finder,
            targets=targets,
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
            try:
                pylint.disable(disabled)
            except UnknownMessageError:
                pass

        sys_paths = finder.sys_paths(filters=self.config['filters'])
        with mod_sys_path(sys_paths):
            pylint.check(targets)

        return reporter.get_issues()

