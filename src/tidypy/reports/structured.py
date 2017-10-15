import csv

from collections import OrderedDict

import pkg_resources

from six import iteritems

from ..util import render_toml, render_json, render_yaml
from .base import Report


class StructuredReport(Report):
    def get_structure(self, collector):
        issues = OrderedDict()
        for filename, file_issues in iteritems(collector.get_grouped_issues()):
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
            ('tidypy', str(pkg_resources.get_distribution('tidypy').version)),
            ('issues', issues),
        ))


class CsvReport(StructuredReport):
    def execute(self, collector):
        issues = self.get_structure(collector)
        writer = csv.writer(self.output_file, lineterminator='\n')
        writer.writerow([
            'filename',
            'line',
            'character',
            'tool',
            'code',
            'message',
        ])

        for filename, file_issues in iteritems(issues['issues']):
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
    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(render_json(issues))


class TomlReport(StructuredReport):
    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(render_toml(issues))


class YamlReport(StructuredReport):
    def execute(self, collector):
        issues = self.get_structure(collector)
        self.output(render_yaml(issues))
