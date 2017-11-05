
from importlib import import_module

from docutils.nodes import system_message
from docutils.parsers.rst import Directive, directives
from docutils.utils import Reporter
from restructuredtext_lint import lint
from six import iteritems

from .base import Tool, Issue, AccessIssue, UnknownIssue, ToolIssue


class DummyDirective(Directive):
    has_content = True

    def run(self):
        return []


class RstLintIssue(Issue):
    tool = 'rstlint'

    @property
    def pylint_type(self):
        if self.code in ('error', 'severe'):
            return 'E'
        return 'W'


class RstLintTool(Tool):
    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.rst$',
        ]
        config['options']['ignore-directives'] = []
        config['options']['load-directives'] = {}
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (level.lower(), level)
            for level in Reporter.levels
        ]

    def execute(self, finder):
        issues = []

        issues.extend(self.load_docutils_directives(finder.project_path))

        for filepath in finder.files(self.config['filters']):
            try:
                errors = lint(
                    finder.read_file(filepath),
                    filepath=filepath,
                )
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
            else:
                issues += [
                    self.make_issue(error, filepath)
                    for error in errors
                ]

        return [
            issue
            for issue in issues
            if issue.code not in self.config['disabled']
        ]

    def load_docutils_directives(self, project_path):
        issues = []

        for name in self.config['options']['ignore-directives']:
            directives.register_directive(name, DummyDirective)
        for name, cls in iteritems(self.config['options']['load-directives']):
            try:
                mod, clazz = cls.rsplit('.', 1)
                clazz = getattr(import_module(mod), clazz)
            except:  # noqa
                issues.append(ToolIssue(
                    'Could not load docutils directive %s' % (cls,),
                    project_path,
                ))
            else:
                directives.register_directive(name, clazz)

        return issues

    def make_issue(self, error, filename):
        if isinstance(error, system_message):
            return RstLintIssue(
                error.type.lower(),
                error.message,
                filename,
                error.line,
            )

        if isinstance(error, EnvironmentError):
            return AccessIssue(error, filename)

        return UnknownIssue(error, filename)

