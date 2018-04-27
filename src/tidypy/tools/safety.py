
from dparse.dependencies import DependencyFile
from packaging.specifiers import SpecifierSet
from safety_db import INSECURE_FULL

from .base import Tool, Issue, AccessIssue, UnknownIssue


CODES = {
    'vulnerable': '"%s" has a known vulnerability: %s',
    'potential':
        '"%s" is known to have past security vulnerabilities, but is not'
        ' pinned to a specific version, so cannot confirm',
}


class SafetyIssue(Issue):
    tool = 'safety'
    pylint_type = 'W'


class SafetyTool(Tool):
    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'requirements\.txt$',
            r'Pipfile$',
            r'Pipfile.lock$',
            r'tox\.ini$',
            r'conda\.yml$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        return sorted(CODES.items())

    def execute(self, finder):
        issues = []

        for filepath in finder.files(self.config['filters']):
            try:
                dep_file = DependencyFile(
                    finder.read_file(filepath),
                    path=filepath,
                )
                dependencies = dep_file.parse().serialize()['dependencies']
            except EnvironmentError as exc:
                issues.append(AccessIssue(exc, filepath))
                continue
            except Exception as exc:  # noqa: broad-except
                issues.append(UnknownIssue(exc, filepath))
                continue

            for dep in dependencies:
                issues.extend(self.find_issues(filepath, dep))

        return [
            issue
            for issue in issues
            if issue.code not in self.config['disabled']
        ]

    def find_issues(self, filepath, dep):
        issues = []

        vulnerabilities = INSECURE_FULL.get(
            dep['name'].replace('_', '-').lower(),
        )
        if not vulnerabilities:
            return issues

        dep_specs = list(dep['specs']._specs)  # noqa: protected-access
        if len(dep_specs) != 1 or dep_specs[0].operator != '==':
            issues.append(SafetyIssue(
                'potential',
                CODES['potential'] % (dep['name'],),
                filepath,
            ))
            return issues

        for vuln in vulnerabilities:
            for specifier in vuln['specs']:
                spec_set = SpecifierSet(specifier)
                if spec_set.contains(dep_specs[0].version):
                    msg = vuln['advisory']
                    if vuln['cve']:
                        msg = '%s: %s' % (vuln['cve'], msg)
                    issues.append(SafetyIssue(
                        'vulnerable',
                        CODES['vulnerable'] % (
                            dep['name'],
                            msg,
                        ),
                        filepath,
                    ))
                    continue

        return issues

