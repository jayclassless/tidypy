
import basicserial

from yamllint import linter
from yamllint.config import YamlLintConfig

from .base import Tool, Issue, AccessIssue, UnknownIssue


class YamlLintIssue(Issue):
    tool = 'yamllint'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pylint_type = 'E' if self.code == 'syntax' else 'C'


class YamlLintTool(Tool):
    """
    The yamllint tool, as its name implies, is a linter for YAML files.
    """

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.yaml$',
            r'\.yml$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        codes = [
            ('syntax', 'YAML syntax error'),
        ]

        cfg = YamlLintConfig('extends: default')
        codes += [
            (rule, rule)
            for rule in cfg.rules
        ]

        return codes

    def make_config(self):
        cfg = 'extends: default\n'

        rules = [
            rule
            for rule, _ in self.get_all_codes()
            if rule != 'syntax'
        ]
        rule_parts = []
        for rule in rules:
            if rule in self.config['disabled']:
                rule_parts.append('  %s: disable' % (rule,))
            elif rule in self.config['options']:
                rule_parts.append('  %s: %s' % (
                    rule,
                    basicserial.to_yaml(self.config['options'][rule]),
                ))

        if rule_parts:
            cfg += 'rules:\n%s' % (
                '\n'.join(rule_parts),
            )

        return YamlLintConfig(cfg)

    def execute(self, finder):
        issues = []
        cfg = self.make_config()

        for filepath in finder.files(self.config['filters']):
            try:
                problems = linter.run(
                    finder.read_file(filepath),
                    cfg,
                    filepath=filepath,
                )
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
            else:
                issues += [
                    self.make_issue(problem, filepath)
                    for problem in problems
                    if not (
                        'syntax' in self.config['disabled']
                        and not problem.rule  # noqa: W503
                    )
                ]
        return issues

    def make_issue(self, problem, filename):
        if isinstance(problem, linter.LintProblem):
            return YamlLintIssue(
                problem.rule or 'syntax',
                problem.desc,
                filename,
                problem.line,
                problem.column,
            )

        if isinstance(problem, EnvironmentError):
            return AccessIssue(problem, filename)

        return UnknownIssue(problem, filename)

