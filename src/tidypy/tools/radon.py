
from __future__ import absolute_import

from radon.complexity import cc_visit
from radon.metrics import mi_visit

from .base import PythonTool, Issue, AccessIssue, ParseIssue


class RadonIssue(Issue):
    tool = 'radon'
    pylint_type = 'W'


TMPL_COMPLEX = '"{entity}" is too complex ({score})'
TMPL_MAINT = 'Module has a low maintainability index ({score:.0f})'


class RadonTool(PythonTool):
    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options'] = {
            'max-complexity': 10,
            'min-maintainability': 20,
        }
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            ('complex', TMPL_COMPLEX),
            ('maintenance', TMPL_MAINT),
        ]

    def execute(self, finder):
        issues = []
        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath)
                issues.extend(self.check_complexity(source, filepath))
                issues.extend(self.check_maintenance(source, filepath))
            except (SyntaxError, TypeError) as exc:
                issues.append(ParseIssue(exc, filepath))
                continue
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

        return issues

    def check_complexity(self, code, filepath):
        issues = []

        if 'complex' in self.config['disabled']:
            return issues

        blocks = cc_visit(code)
        for block in blocks:
            if block.complexity > self.config['options']['max-complexity']:
                issues.append(RadonIssue(
                    'complex',
                    TMPL_COMPLEX.format(
                        entity=block.name,
                        score=block.complexity,
                    ),
                    filepath,
                    block.lineno,
                    block.col_offset + 1,
                ))

        return issues

    def check_maintenance(self, code, filepath):
        issues = []

        if 'maintenance' in self.config['disabled']:
            return issues

        score = mi_visit(code, False)
        if score < self.config['options']['min-maintainability']:
            issues.append(RadonIssue(
                'maintenance',
                TMPL_MAINT.format(
                    score=score,
                ),
                filepath,
                1,
            ))

        return issues

