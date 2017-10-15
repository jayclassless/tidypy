
from collections import OrderedDict
from threading import Lock

from six import iteritems, itervalues


DEFAULT_SORT = ('filename', 'line', 'character', 'tool', 'code')


def default_group(issue):  # noqa
    return issue.filename


class Collector(object):
    def __init__(self, config):
        self.config = config
        self.all_issues = []
        self._lock = Lock()

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
            sortby = DEFAULT_SORT
        return self._group_issues(self.get_issues(), keyfunc, sortby)

    def sort_issues(self, issues, attrs=None):
        if attrs is None:
            attrs = DEFAULT_SORT

        for attr in reversed(attrs):
            if attr in ('line', 'character'):
                keyfunc = lambda i, attr=attr: getattr(i, attr) or 0
            else:
                keyfunc = lambda i, attr=attr: getattr(i, attr) or ''

            issues = sorted(issues, key=keyfunc)

        return issues

    def _group_issues(self, issues, keyfunc, sortby):
        grouped = OrderedDict()

        for issue in issues:
            key = keyfunc(issue)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(issue)

        for group, group_issues in iteritems(grouped):
            grouped[group] = self.sort_issues(group_issues, sortby)

        return grouped

    def _merge_issues(self):
        issues = self.all_issues

        # If merging is disabled, let's bail out here
        if not self.config['merge_issues']:
            return issues

        # Group the issues by file & line
        grouped = self._group_issues(
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

