
import sys

from tidypy import execute_reports, get_default_config, Collector, TidyPyIssue


ISSUES = [
    TidyPyIssue(
        'code1',
        'Message 1',
        'someproject/foo.py',
        5,
        23,
    ),
    TidyPyIssue(
        'code2',
        'Message 2',
        'someproject/foo.py',
        2,
    ),
    TidyPyIssue(
        'code1',
        'Message 1',
        'someproject/blah/bar.py',
        28,
    ),
    TidyPyIssue(
        'code3',
        'Message 3',
        'someproject/subdir/foobar.json',
        5,
        23,
    ),
    TidyPyIssue(
        'code5',
        'Message 5\nHas some newlines\nLike these',
        'someproject/baz.py',
        33,
    ),
]


EXPECTED_CONSOLE = u'''baz.py (1)
   33     Message 5
          Has some newlines
          Like these
          (tidypy:code5)

blah/bar.py (1)
   28     Message 1 (tidypy:code1)

foo.py (2)
    2     Message 2 (tidypy:code2)
    5:23  Message 1 (tidypy:code1)

subdir/foobar.json (1)
    5:23  Message 3 (tidypy:code3)

\u2717 5 issues found.
'''


def test_console_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'console'}]

    collector = Collector(cfg)

    execute_reports(cfg, 'someproject', collector)

    if sys.platform == 'win32':
        expected = u'No issues found!\r\n'
    else:
        expected = u'\u2714 No issues found!\n'

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


    collector.add_issues(ISSUES)
    execute_reports(cfg, 'someproject', collector)

    expected = EXPECTED_CONSOLE
    if sys.platform == 'win32':
        expected = expected.replace(u'\u2717 ', '').replace('\n', '\r\n')

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''

