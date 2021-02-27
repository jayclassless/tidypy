
from detect_secrets import SecretsCollection
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.core.plugins.util import \
    get_mapping_from_secret_type_to_class
from detect_secrets.settings import transient_settings

from .base import Tool, Issue, AccessIssue, UnknownIssue


class DetectSecretsIssue(Issue):
    tool = 'secrets'
    pylint_type = 'W'


PLUGINS = tuple(get_mapping_from_secret_type_to_class().values())

DESCRIPTION = 'Possible secret detected: {description}'


class DetectSecretsTool(Tool):
    """
    The secrets tool attempts to detect secrets (keys, passwords, etc) that are
    embedded in your codebase.
    """

    @classmethod
    def get_all_codes(cls):
        return [
            (
                plugin.__name__,
                plugin.secret_type,
            )
            for plugin in PLUGINS
        ]

    def execute(self, finder):
        issues = []

        settings = {
            'plugins_used': [
                {'name': plugin.__name__}
                for plugin in PLUGINS
                if plugin.__name__ not in self.config['disabled']
            ],
        }

        detector = SecretsCollection()
        with transient_settings(settings):
            for filepath in finder.files(self.config['filters']):
                try:
                    detector.scan_file(filepath)
                except Exception as exc:  # pylint: disable=broad-except
                    issues.append(self.make_issue(exc, filepath))

            for filepath, problem in detector:
                issues.append(self.make_issue(problem, filepath))

        return issues

    def make_issue(self, problem, filename):
        if isinstance(problem, PotentialSecret):
            plugin = [
                plugin
                for plugin in PLUGINS
                if plugin.secret_type == problem.type
            ][0]
            return DetectSecretsIssue(
                plugin.__name__,
                DESCRIPTION.format(description=problem.type),
                filename,
                problem.line_number,
            )

        if isinstance(problem, EnvironmentError):
            return AccessIssue(problem, filename)

        return UnknownIssue(problem, filename)

