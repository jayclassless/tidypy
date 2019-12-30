
from dennis.linter import (
    Linter,
    LintMessage,
    get_lint_rules as get_linter_rules,
)
from dennis.templatelinter import (
    TemplateLinter,
    get_lint_rules as get_template_linter_rules,
)
from dennis.tools import get_available_formats

from .base import Tool, Issue, AccessIssue, UnknownIssue, ParseIssue


class PoLintIssue(Issue):
    tool = 'polint'


class PoLintTool(Tool):
    """
    A part of the dennis package, this tool lints PO and POT files for
    problems.
    """

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.pot?$',
        ]
        config['options'] = {
            'variable-formats': list(get_available_formats()),
        }
        return config

    @classmethod
    def get_all_codes(cls):
        codes = []

        for rule in get_linter_rules().values():
            codes.append((
                rule.num,
                rule.desc,
            ))

        for rule in get_template_linter_rules().values():
            codes.append((
                rule.num,
                rule.desc,
            ))

        return codes

    def execute(self, finder):
        issues = []

        rules = [
            rule
            for rule, _ in self.get_all_codes()
            if rule not in self.config['disabled']
        ]
        linter = Linter(self.config['options']['variable-formats'], rules)
        tmpl_linter = TemplateLinter(
            self.config['options']['variable-formats'],
            rules,
        )

        for filepath in finder.files(self.config['filters']):
            try:
                file_content = finder.read_file(filepath)
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
                continue

            try:
                if filepath.endswith('.po'):
                    errors = linter.verify_file(file_content)
                elif filepath.endswith('.pot'):
                    errors = tmpl_linter.verify_file(file_content)
            except IOError as exc:
                issues.append(ParseIssue(exc, filepath))
                continue
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
                continue

            issues += [
                self.make_issue(error, filepath)
                for error in errors
            ]

        return issues

    def make_issue(self, error, filename):
        if isinstance(error, LintMessage):
            issue = PoLintIssue(
                error.code,
                error.msg,
                filename,
                error.line + 1,
            )
            if error.kind == 'err':
                issue.pylint_type = 'E'
            else:
                issue.pylint_type = 'W'
            return issue

        if isinstance(error, EnvironmentError):
            return AccessIssue(error, filename)

        return UnknownIssue(error, filename)

