
from tidypy import execute_reports, get_default_config, Collector, TidyPyIssue


ISSUES = [
    TidyPyIssue(
        'code1',
        'Message 1',
        u'someproject/foo.py',
        5,
        23,
    ),
    TidyPyIssue(
        'code2',
        'Message 2',
        u'someproject/foo.py',
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


def test_json_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'json'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''{
  "tidypy": "0.2.0",
  "issues": {
    "blah/bar.py": [
      {
        "line": 28,
        "character": 0,
        "code": "code1",
        "tool": "tidypy",
        "message": "Message 1"
      }
    ],
    "foo.py": [
      {
        "line": 2,
        "character": 0,
        "code": "code2",
        "tool": "tidypy",
        "message": "Message 2"
      },
      {
        "line": 5,
        "character": 23,
        "code": "code1",
        "tool": "tidypy",
        "message": "Message 1"
      }
    ],
    "subdir/foobar.json": [
      {
        "line": 5,
        "character": 23,
        "code": "code3",
        "tool": "tidypy",
        "message": "Message 3"
      }
    ]
  }
}
'''

    out, err = capsys.readouterr()
    assert expected == out
    assert err == ''


def test_toml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'toml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''tidypy = "0.2.0"

[issues]

[[issues."blah/bar.py"]]
line = 28
character = 0
code = "code1"
tool = "tidypy"
message = "Message 1"

[[issues."foo.py"]]
line = 2
character = 0
code = "code2"
tool = "tidypy"
message = "Message 2"

[[issues."foo.py"]]
line = 5
character = 23
code = "code1"
tool = "tidypy"
message = "Message 1"

[[issues."subdir/foobar.json"]]
line = 5
character = 23
code = "code3"
tool = "tidypy"
message = "Message 3"

'''

    out, err = capsys.readouterr()
    assert expected == out
    assert err == ''


def test_yaml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'yaml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''tidypy: 0.2.0
issues:
  blah/bar.py:
  - line: 28
    character: 0
    code: code1
    tool: tidypy
    message: Message 1
  foo.py:
  - line: 2
    character: 0
    code: code2
    tool: tidypy
    message: Message 2
  - line: 5
    character: 23
    code: code1
    tool: tidypy
    message: Message 1
  subdir/foobar.json:
  - line: 5
    character: 23
    code: code3
    tool: tidypy
    message: Message 3
'''

    out, err = capsys.readouterr()
    assert expected == out
    assert err == ''


def test_csv_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'csv'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''filename,line,character,tool,code,message
blah/bar.py,28,0,tidypy,code1,Message 1
foo.py,2,0,tidypy,code2,Message 2
foo.py,5,23,tidypy,code1,Message 1
subdir/foobar.json,5,23,tidypy,code3,Message 3
'''

    out, err = capsys.readouterr()
    assert expected == out
    assert err == ''

