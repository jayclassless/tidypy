from __future__ import absolute_import

import ast

from vulture import Vulture
from vulture.core import ENCODING_REGEX
from vulture.utils import VultureInputException

from .base import PythonTool, Issue, ParseIssue, AccessIssue


class VultureIssue(Issue):
    tool = 'vulture'
    pylint_type = 'R'


class TidyPyVulture(Vulture):
    ISSUE_TYPES = (
        ('unused-class', 'Unused class {entity}', 'unused_classes'),
        ('unused-function', 'Unused function {entity}', 'unused_funcs'),
        ('unused-import', 'Unused import {entity}', 'unused_imports'),
        ('unused-property', 'Unused property {entity}', 'unused_props'),
        ('unused-variable', 'Unused variable {entity}', 'unused_vars'),
        ('unused-attribute', 'Unused attribute {entity}', 'unused_attrs')
    )

    def __init__(self, config):
        super(TidyPyVulture, self).__init__()
        self.config = config
        self._tidypy_issues = []

    def scavenge(self, finder):  # pylint: disable=arguments-differ
        self._tidypy_issues = []

        if self.config['options']['whitelist']:
            self.scan(
                '\n'.join(self.config['options']['whitelist']),
                filename='VultureWhitelist',
            )

        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath)
            except VultureInputException as exc:
                self._tidypy_issues.append(ParseIssue(exc, filepath))
                continue
            except EnvironmentError as exc:
                self._tidypy_issues.append(AccessIssue(exc, filepath))
                continue

            self.scan(source, filename=filepath)

    # Unfortunately instead of raising exceptions, this base implementation of
    # this method writes directly to stdout. This is a copy&paste with that
    # piece replaced by capturing an issue
    def scan(self, code, filename=''):
        code = ENCODING_REGEX.sub("", code, count=1)
        self.code = code.splitlines()
        self.filename = filename
        try:
            node = ast.parse(code, filename=self.filename)
        except SyntaxError as err:
            self._tidypy_issues.append(ParseIssue(err, filename))
        else:
            self.visit(node)

    def get_issues(self):
        issues = []

        for code, template, prop_name in self.ISSUE_TYPES:
            if code in self.config['disabled']:
                continue

            for item in getattr(self, prop_name):
                try:
                    filename = item.file
                except AttributeError:
                    filename = item.filename

                issues.append(VultureIssue(
                    code,
                    template.format(entity=str(item)),
                    filename,
                    item.first_lineno,
                ))

        return self._tidypy_issues + issues


class VultureTool(PythonTool):
    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options']['whitelist'] = []
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (code, tmpl)
            for code, tmpl, _ in TidyPyVulture.ISSUE_TYPES
        ]

    def __init__(self, *args, **kwargs):
        super(VultureTool, self).__init__(*args, **kwargs)
        self.vulture = TidyPyVulture(self.config)

    def execute(self, finder):
        self.vulture.scavenge(finder)
        return self.vulture.get_issues()

