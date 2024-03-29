
import re

from collections import OrderedDict, defaultdict
from threading import Lock

from .util import read_file


RE_PYTHON_FILE = re.compile(r'\.py$')

RE_NOQA = re.compile(
    r'# noqa(?:: (?P<codes>([a-z0-9-:@]+(?:[,\s]+)?)+))?',
    re.IGNORECASE,
)


def default_group(issue):  # noqa
    return issue.filename


class Collector:
    """
    A class that contains all the issues found during an execution of the
    TidyPy tool suite.
    """

    NO_SORT = ()
    DEFAULT_SORT = ('filename', 'line', 'character', 'tool', 'code')

    def __init__(self, config):
        """
        :param config:
            the configuration used to during the analysis of the project
        :type config: dict
        """

        self._config = config
        self._all_issues = []
        self._cleaned_issues = None
        self._lock = Lock()
        self._noqa = {}

    def add_issues(self, issues):
        """
        Adds an issue to the collection.

        :param issues: the issue(s) to add
        :type issues: tidypy.Issue or list(tidypy.Issue)
        """

        if not isinstance(issues, (list, tuple)):
            issues = [issues]
        with self._lock:
            self._all_issues.extend(issues)
            self._cleaned_issues = None

    def issue_count(self, include_unclean=False):
        """
        Returns the number of issues in the collection.

        :param include_unclean:
            whether or not to include issues that are being ignored due to
            being a duplicate, excluded, etc.
        :type include_unclean: bool
        :rtype: int
        """

        if include_unclean:
            return len(self._all_issues)
        self._ensure_cleaned_issues()
        return len(self._cleaned_issues)

    def get_issues(self, sortby=None):
        """
        Retrieves the issues in the collection.

        :param sortby: the properties to sort the issues by
        :type sortby: list(str)
        :rtype: list(tidypy.Issue)
        """

        self._ensure_cleaned_issues()
        return self._sort_issues(self._cleaned_issues, sortby)

    def get_grouped_issues(self, keyfunc=None, sortby=None):
        """
        Retrieves the issues in the collection grouped into buckets according
        to the key generated by the keyfunc.

        :param keyfunc:
            a function that will be used to generate the key that identifies
            the group that an issue will be assigned to. This function receives
            a single tidypy.Issue argument and must return a string. If not
            specified, the filename of the issue will be used.
        :type keyfunc: func
        :param sortby: the properties to sort the issues by
        :type sortby: list(str)
        :rtype: OrderedDict
        """

        if not keyfunc:
            keyfunc = default_group
        if not sortby:
            sortby = self.DEFAULT_SORT
        self._ensure_cleaned_issues()
        return self._group_issues(self._cleaned_issues, keyfunc, sortby)

    def _sort_issues(self, issues, sortby=None):
        if sortby is None:
            sortby = self.DEFAULT_SORT

        for attr in reversed(sortby):
            if attr in ('line', 'character'):
                keyfunc = lambda i, attr=attr: getattr(i, attr) or 0
            else:
                keyfunc = lambda i, attr=attr: getattr(i, attr) or ''

            issues = sorted(issues, key=keyfunc)

        return issues

    def _group_issues(self, issues, keyfunc, sortby):
        grouped = defaultdict(list)
        for issue in issues:
            grouped[keyfunc(issue)].append(issue)

        return OrderedDict([
            (key, self._sort_issues(grouped[key], sortby))
            for key in sorted(grouped)
        ])

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

    def _ensure_cleaned_issues(self):
        if self._cleaned_issues is None:
            self._cleaned_issues = self._clean_issues(self._all_issues)

    def _clean_issues(self, issues):
        # Filter out disabled tidypy issues
        issues = [
            issue
            for issue in issues
            if issue.tool != 'tidypy' or (
                issue.tool == 'tidypy'
                and issue.code not in self._config['disabled']  # noqa: W503
            )
        ]

        # Filter out issues for lines marked with "noqa"
        if self._config['noqa']:
            issues = [
                issue
                for issue in issues
                if not self._is_noqa(issue)
            ]

        # If merging is disabled, let's bail out here
        if not self._config['merge-issues']:
            return issues

        # Group the issues by file & line
        grouped = self._group_issues(
            issues,
            lambda x: '%s|%s' % (x.filename, x.line),
            ('tool', 'code', 'character'),
        )
        issues = []
        for group in grouped.values():
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

