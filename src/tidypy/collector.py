
import re

from collections import OrderedDict
from threading import Lock

from six import iteritems, itervalues

from .util import read_file


RE_PYTHON_FILE = re.compile(r'\.py$')

RE_NOQA = re.compile(
    r'# noqa(?:: (?P<codes>([a-zA-Z0-9-:@]+(?:[,\s]+)?)+))?',
    re.IGNORECASE,
)


def default_group(issue):  # noqa
    return issue.filename


class Collector(object):
    NO_SORT = ()
    DEFAULT_SORT = ('filename', 'line', 'character', 'tool', 'code')

    def __init__(self, config):
        self.config = config
        self.all_issues = []
        self._lock = Lock()
        self._noqa = {}

    def add_issues(self, issues):
        if not isinstance(issues, (list, tuple)):
            issues = [issues]
        with self._lock:
            self.all_issues.extend([
                issue
                for issue in issues
                if issue.tool != 'tidypy' or (
                    issue.tool == 'tidypy' and
                    issue.code not in self.config['disabled']
                )
            ])

    def get_issues(self, sortby=None):
        issues = self._merge_issues()
        return self.sort_issues(issues, sortby)

    def get_grouped_issues(self, keyfunc=None, sortby=None):
        if not keyfunc:
            keyfunc = default_group
        if not sortby:
            sortby = self.DEFAULT_SORT
        return self.group_issues(self.get_issues(), keyfunc, sortby)

    def sort_issues(self, issues, attrs=None):
        if attrs is None:
            attrs = self.DEFAULT_SORT

        for attr in reversed(attrs):
            if attr in ('line', 'character'):
                keyfunc = lambda i, attr=attr: getattr(i, attr) or 0
            else:
                keyfunc = lambda i, attr=attr: getattr(i, attr) or ''

            issues = sorted(issues, key=keyfunc)

        return issues

    def group_issues(self, issues, keyfunc, sortby):
        grouped = OrderedDict()

        for issue in issues:
            key = keyfunc(issue)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(issue)

        for group, group_issues in iteritems(grouped):
            grouped[group] = self.sort_issues(group_issues, sortby)

        return grouped

    def _parse_noqa(self, filename):
        lines = {}

        if not RE_PYTHON_FILE.search(filename):
            return lines

        try:
            content = read_file(filename)
        except EnvironmentError:
            return lines

        for idx, line in enumerate(content.splitlines()):
            match = RE_NOQA.search(line)
            if not match:
                continue

            if match.groupdict()['codes']:
                lines[idx + 1] = match.groupdict()['codes'].split(',')
            else:
                lines[idx + 1] = 'ALL'

        return lines

    def _is_noqa(self, issue):
        if issue.filename not in self._noqa:
            self._noqa[issue.filename] = self._parse_noqa(issue.filename)

        if issue.line not in self._noqa[issue.filename]:
            return False

        codes = self._noqa[issue.filename][issue.line]
        if codes == 'ALL':
            return True

        return issue.code in codes \
            or ('@%s' % (issue.tool,)) in codes \
            or ('%s:%s' % (issue.tool, issue.code)) in codes

    def _merge_issues(self):
        issues = self.all_issues

        # Filter out issues for lines marked with "noqa"
        if self.config['noqa']:
            issues = [
                issue
                for issue in issues
                if not self._is_noqa(issue)
            ]

        # If merging is disabled, let's bail out here
        if not self.config['merge_issues']:
            return issues

        # Group the issues by file & line
        grouped = self.group_issues(
            issues,
            lambda x: '%s|%s' % (x.filename, x.line),
            ('tool', 'code', 'character'),
        )
        issues = []
        for group in itervalues(grouped):
            issues.extend(self._merge_group(group))

        return issues

    def _merge_group(self, issues):
        # Strip out dupes
        deduped = []
        last = (None, None)
        for issue in issues:
            this = (issue.tool, issue.code)
            if this != last:
                last = this
                deduped.append(issue)
        issues = deduped

        return issues

