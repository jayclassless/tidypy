
from demjson import decode, JSONError

from .base import Tool, Issue, AccessIssue, UnknownIssue


class JsonLintIssue(Issue):
    tool = 'jsonlint'
    pylint_type = 'E'


class JsonLintTool(Tool):
    """
    A part of the demjson package, this tool validates your JSON documents for
    strict conformance to the JSON specification, and to detect potential data
    portability issues.
    """

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.json$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (sev, sev)
            for sev in JSONError.severities
        ]

    def execute(self, finder):
        issues = []

        for filepath in finder.files(self.config['filters']):
            try:
                results = decode(
                    finder.read_file(filepath),
                    strict=True,
                    return_errors=True,
                )
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))
            else:
                issues += [
                    self.make_issue(error, filepath)
                    for error in results.errors
                ]

        return [
            issue
            for issue in issues
            if issue.code not in self.config['disabled']
        ]

    def make_issue(self, error, filename):
        if isinstance(error, JSONError):
            return JsonLintIssue(
                error.severity,
                error.message,
                filename,
                error.position.line,
                error.position.column + 1,
            )

        if isinstance(error, EnvironmentError):
            return AccessIssue(error, filename)

        return UnknownIssue(error, filename)

