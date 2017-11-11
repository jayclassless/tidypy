
from __future__ import absolute_import

import ast

from mccabe import PathGraphingAstVisitor
from six import itervalues

from .base import PythonTool, Issue, AccessIssue, ParseIssue


class McCabeIssue(Issue):
    tool = 'mccabe'
    pylint_type = 'W'


TMPL_COMPLEX = '"{entity}" is too complex ({score})'


class McCabeTool(PythonTool):
    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options'] = {
            'max-complexity': 10,
        }
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            ('complex', TMPL_COMPLEX),
        ]

    def execute(self, finder):
        issues = []

        if 'complex' in self.config['disabled']:
            return issues

        for filepath in finder.files(self.config['filters']):
            try:
                source = finder.read_file(filepath)
                tree = ast.parse(
                    source,
                    filename=filepath,
                )
            except (SyntaxError, TypeError) as exc:
                issues.append(ParseIssue(exc, filepath))
                continue
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

            visitor = PathGraphingAstVisitor()
            visitor.preorder(tree, visitor)

            for graph in itervalues(visitor.graphs):
                complexity = graph.complexity()
                if complexity > self.config['options']['max-complexity']:
                    issues.append(McCabeIssue(
                        'complex',
                        TMPL_COMPLEX.format(
                            entity=graph.entity,
                            score=complexity,
                        ),
                        filepath,
                        graph.lineno,
                        graph.column + 1,
                    ))

        return issues

