
import warnings

from pydiatra.checks import check_source

from .base import PythonTool, Issue, AccessIssue


class PyDiatraIssue(Issue):
    tool = 'pydiatra'


class PyDiatraTool(PythonTool):
    """
    pydiatra is yet another static checker for Python code.
    """

    @classmethod
    def get_all_codes(cls):
        # Not currently a way to introspect all the codes pydiatra can return
        return []

    def execute(self, finder):
        issues = []

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for filepath in finder.files(self.config['filters']):
                try:
                    source = finder.read_file(filepath)
                except EnvironmentError as exc:
                    issues.append(
                        AccessIssue(exc, filepath)
                    )
                else:
                    for tag in check_source(str(filepath), source):
                        issues.append(self.make_issue(filepath, tag))

        return [
            issue
            for issue in issues
            if issue.code not in self.config['disabled']
        ]

    def make_issue(self, filepath, tag):
        return PyDiatraIssue(
            tag.args[0],
            ' '.join(tag.args[1:]) or tag.args[0],
            filepath,
            tag.lineno,
        )

