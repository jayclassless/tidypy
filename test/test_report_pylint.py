
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


EXPECTED_PYLINT = '''************* Module blah.bar
F: 28, 0: Message 1 (code1@tidypy)
************* Module foo
F:  2, 0: Message 2 (code2@tidypy)
F:  5,22: Message 1 (code1@tidypy)
************* Module subdir/foobar.json
F:  5,22: Message 3 (code3@tidypy)
'''


def test_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'pylint'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert out.replace('\r\n', '\n') == EXPECTED_PYLINT
    assert err == ''
