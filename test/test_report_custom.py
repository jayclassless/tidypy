
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



EXPECTED = '''blah/bar.py/28/0/tidypy/code1/Message 1
foo.py/2/0/tidypy/code2/Message 2
foo.py/5/23/tidypy/code1/Message 1
subdir/foobar.json/5/23/tidypy/code3/Message 3
'''


def test_execute(capsys):
    cfg = get_default_config()
    cfg['requested_reports'] = [{
        'type': 'custom',
        'format': '{filename}/{line}/{character}/{tool}/{code}/{message}'
    }]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert out.replace('\r\n', '\n') == EXPECTED
    assert err == ''


def test_execute_bad_format(capsys):
    cfg = get_default_config()
    cfg['requested_reports'] = [{
        'type': 'custom',
        'format': '{filename:,}/{line}'
    }]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert out == ''
    assert err.strip() == "Invalid format for custom report: Cannot specify ',' with 's'."


def test_execute_bad_token(capsys):
    cfg = get_default_config()
    cfg['requested_reports'] = [{
        'type': 'custom',
        'format': '{filename}/{foo}'
    }]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert out == ''
    assert err.strip() == "Invalid format for custom report: Unknown token 'foo'"

