
from __future__ import absolute_import

from detect_secrets.core.usage import PluginOptions
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.core.initialize import from_plugin_classname
from six import iteritems

from .base import Tool, Issue, AccessIssue, UnknownIssue


class DetectSecretsIssue(Issue):
    tool = 'secrets'
    pylint_type = 'W'


CODE = 'secret'
DESCRIPTION = 'Possible secret detected: %s'


class DetectSecretsTool(Tool):
    """
    The secrets tool attempts to detect secrets (keys, passwords, etc) that are
    embedded in your codebase.
    """

    @classmethod
    def get_all_codes(cls):
        return [(CODE, DESCRIPTION)]

    def execute(self, finder):
        issues = []

        plugins = [
            from_plugin_classname(plugin.classname, **dict([
                (
                    arg[0][2:].replace('-', '_'),
                    arg[1],
                )
                for arg in plugin.related_args
            ]))
            for plugin in PluginOptions.all_plugins
        ]
        detector = SecretsCollection(plugins)

        for filepath in finder.files(self.config['filters']):
            try:
                detector.scan_file(filepath)
            except Exception as exc:  # pylint: disable=broad-except
                issues.append(self.make_issue(exc, filepath))

        for filepath, problems in iteritems(detector.data):
            for problem in problems:
                issues.append(self.make_issue(problem, filepath))

        return issues

    def make_issue(self, problem, filename):
        if isinstance(problem, PotentialSecret):
            return DetectSecretsIssue(
                CODE,
                DESCRIPTION % (problem.type,),
                filename,
                problem.lineno,
            )

        if isinstance(problem, EnvironmentError):
            return AccessIssue(problem, filename)

        return UnknownIssue(problem, filename)

