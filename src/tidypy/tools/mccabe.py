
from mccabe import PathGraphingAstVisitor

from .base import PythonTool, Issue, AccessIssue, ParseIssue
from ..util import parse_python_file


class McCabeIssue(Issue):
    tool = 'mccabe'
    pylint_type = 'W'


CODE = 'complex'
DESCRIPTION = '"{entity}" is too complex ({score})'


class McCabeTool(PythonTool):
    """
    Ned Batchelder's script to check the McCabe the cyclomatic complexity of
    Python code.
    """

    @classmethod
    def get_default_config(cls):
        config = PythonTool.get_default_config()
        config['options'] = {
            'max-complexity': 10,
        }
        return config

    @classmethod
    def get_all_codes(cls):
        return [(CODE, DESCRIPTION)]

    def execute(self, finder):
        issues = []
        if CODE in self.config['disabled']:
            return issues

        for filepath in finder.files(self.config['filters']):
            try:
                tree = parse_python_file(filepath)
            except (SyntaxError, TypeError) as exc:
                issues.append(ParseIssue(exc, filepath))
                continue
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue

            visitor = PathGraphingAstVisitor()
            visitor.preorder(tree, visitor)

            for graph in visitor.graphs.values():
                complexity = graph.complexity()
                if complexity > self.config['options']['max-complexity']:
                    issues.append(McCabeIssue(
                        'complex',
                        DESCRIPTION.format(
                            entity=graph.entity,
                            score=complexity,
                        ),
                        filepath,
                        graph.lineno,
                        graph.column + 1,
                    ))

        return issues

