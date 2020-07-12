
import os

from importlib import import_module
from shutil import rmtree
from tempfile import mkdtemp

from docutils.nodes import system_message
from docutils.parsers.rst import Directive, directives, roles
from docutils.utils import Reporter
from restructuredtext_lint import lint

from .base import Tool, Issue, AccessIssue, UnknownIssue, ToolIssue


class DummyDirective(Directive):
    has_content = True

    def run(self, *args, **kwargs):
        # pylint: disable=unused-argument
        return []


def dummy_role(*args, **kwargs):
    # pylint: disable=unused-argument
    return [], []


dummy_role.content = True


class RstLintIssue(Issue):
    tool = 'rstlint'

    @property
    def pylint_type(self):
        if self.code in ('error', 'severe'):
            return 'E'
        return 'W'


class RstLintTool(Tool):
    """
    The restructuredtext-lint tool, as its name implies, is a linter for
    reStructuredText files.
    """

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.rst$',
        ]
        config['options']['ignore-directives'] = []
        config['options']['ignore-roles'] = []
        config['options']['load-directives'] = {}
        config['options']['sphinx-extensions'] = None
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (level.lower(), level)
            for level in Reporter.levels
        ]

    def execute(self, finder):
        issues = []

        issues.extend(self.load_docutils_shims(finder.project_path))

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

    def load_docutils_shims(self, project_path):
        issues = []

        for name in self.config['options']['ignore-directives']:
            directives.register_directive(name, DummyDirective)

        for name in self.config['options']['ignore-roles']:
            roles.register_local_role(name, dummy_role)

        failed = []
        for name, cls in self.config['options']['load-directives'].items():
            try:
                mod, clazz = cls.rsplit('.', 1)
                clazz = getattr(import_module(mod), clazz)
            except:  # noqa
                failed.append(cls)
            else:
                directives.register_directive(name, clazz)
        if failed:
            issues.append(ToolIssue(
                'rstlint: Could not load docutils directives: %s' % (
                    ', '.join(failed),
                ),
                project_path,
            ))

        if self.config['options']['sphinx-extensions'] is not None:
            issues.extend(self.load_sphinx(project_path))

        return issues

    def load_sphinx(self, project_path):
        issues = []

        try:
            from sphinx.application import Sphinx  # noqa: import-outside-toplevel
        except ImportError:
            Sphinx = None  # noqa: N806

        if Sphinx:
            register_directive = directives.register_directive
            register_local_role = roles.register_local_role

            def hijacked_directive(name, *args, **kwargs):
                # pylint: disable=unused-argument
                register_directive(name, DummyDirective)

            def hijacked_role(name, *args, **kwargs):
                # pylint: disable=unused-argument
                register_local_role(name, dummy_role)

            directives.register_directive = hijacked_directive
            roles.register_local_role = hijacked_role

            tmp_dir_in = mkdtemp()
            tmp_dir_out = mkdtemp()
            try:
                with open(os.path.join(tmp_dir_in, 'conf.py'), 'w') as conf:
                    conf.write('extensions = %r' % (
                        self.config['options']['sphinx-extensions'],
                    ))
                Sphinx(
                    tmp_dir_in, tmp_dir_in,
                    tmp_dir_out, tmp_dir_out,
                    None, status=None,
                )
            finally:
                rmtree(tmp_dir_in)
                rmtree(tmp_dir_out)

            directives.register_directive = register_directive
            roles.register_local_role = register_local_role

        else:
            issues.append(ToolIssue(
                'rstlint: Sphinx not found in the environment -- cannot load'
                ' extensions',
                project_path,
            ))

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

