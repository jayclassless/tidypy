
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
]


def test_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'pycodestyle'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''blah/bar.py:28:0 code1@tidypy Message 1
foo.py:2:0 code2@tidypy Message 2
foo.py:5:23 code1@tidypy Message 1
subdir/foobar.json:5:23 code3@tidypy Message 3
'''

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''

