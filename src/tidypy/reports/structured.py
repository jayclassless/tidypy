
import csv

from collections import OrderedDict

import basicserial
import pkg_resources

from .base import Report


class StructuredReport(Report):
    def get_structure(self, collector):
        issues = OrderedDict()
        for filename, file_issues in collector.get_grouped_issues().items():
            issues[self.relative_filename(filename)] = [
                OrderedDict((
                    ('line', issue.line),
                    ('character', issue.character or 0),
                    ('code', issue.code),
                    ('tool', issue.tool),
                    ('message', issue.message),
                ))
                for issue in file_issues
            ]

        return OrderedDict((
            (
                'tidypy',
                str(pkg_resources.get_distribution('tidypy').version),
            ),
            ('issues', issues),
        ))


class CsvReport(StructuredReport):
    """
    Generates a set of CSV records that contains the results of the analysis.
    """

    def execute(self, collector):
        issues = self.get_structure(collector)
        writer = csv.writer(self.output_file, lineterminator=u'\n')  # noqa: @2to3
        writer.writerow([
            'filename',
            'line',
            'character',
            'tool',
            'code',
            'message',
        ])

        for filename, file_issues in issues['issues'].items():
            for issue in file_issues:
                writer.writerow([
                    filename,
                    issue['line'],
                    issue['character'],
                    issue['tool'],
                    issue['code'],
                    issue['message'],
                ])


class JsonReport(StructuredReport):
    """
    Generates a JSON-serialized object that contains the results of the
    analysis.
    """

    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(basicserial.to_json(issues, pretty=True))


class TomlReport(StructuredReport):
    """
    Generates a TOML-serialized object that contains the results of the
    analysis.
    """

    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(basicserial.to_toml(issues, pretty=True))


class YamlReport(StructuredReport):
    """
    Generates a YAML-serialized object that contains the results of the
    analysis.
    """

    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(basicserial.to_yaml(issues, pretty=True))

