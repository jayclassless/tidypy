
from detect_secrets.core.usage import get_all_plugin_descriptors
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.common.initialize import from_plugin_classname

from .base import Tool, Issue, AccessIssue, UnknownIssue


class DetectSecretsIssue(Issue):
    tool = 'secrets'
    pylint_type = 'W'


PLUGINS = [
    from_plugin_classname(_plugin.classname, (), **dict([
        (
            _arg[0][2:].replace('-', '_'),
            _arg[1],
        )
        for _arg in _plugin.related_args
    ]))
    for _plugin in get_all_plugin_descriptors(())
]

DESCRIPTION = 'Possible secret detected: {description}'


def plugin_code(plugin):
    return plugin.__class__.__name__


class DetectSecretsTool(Tool):
    """
    The secrets tool attempts to detect secrets (keys, passwords, etc) that are
    embedded in your codebase.
    """

    @classmethod
    def get_all_codes(cls):
        return [
            (
                plugin_code(plugin),
                plugin.secret_type,
            )
            for plugin in PLUGINS
        ]

    def execute(self, finder):
        issues = []

        plugins = [
            plugin
            for plugin in PLUGINS
            if plugin_code(plugin) not in self.config['disabled']
        ]

        detector = SecretsCollection(plugins)

        for filepath in finder.files(self.config['filters']):
            try:
                detector.scan_file(filepath)
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))

        for filepath, problems in detector.data.items():
            for problem in problems:
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
                plugin_code(plugin),
                DESCRIPTION.format(description=problem.type),
                filename,
                problem.lineno,
            )

        if isinstance(problem, EnvironmentError):
            return AccessIssue(problem, filename)

        return UnknownIssue(problem, filename)

