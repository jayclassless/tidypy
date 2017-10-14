
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
  "issues": {
    "foo.py": [
      {
        "message": "Message 2",
        "line": 2,
        "code": "code2",
        "character": 0,
        "tool": "tidypy"
      },
      {
        "message": "Message 1",
        "line": 5,
        "code": "code1",
        "character": 23,
        "tool": "tidypy"
      }
    ],
    "subdir/foobar.json": [
      {
        "message": "Message 3",
        "line": 5,
        "code": "code3",
        "character": 23,
        "tool": "tidypy"
      }
    ],
    "blah/bar.py": [
      {
        "message": "Message 1",
        "line": 28,
        "code": "code1",
        "character": 0,
        "tool": "tidypy"
      }
    ]
  },
  "tidypy": "0.1.0"
}
'''

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


def test_toml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'toml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''tidypy = "0.1.0"

[issues]

[[issues."foo.py"]]
message = "Message 2"
line = 2
code = "code2"
character = 0
tool = "tidypy"

[[issues."foo.py"]]
message = "Message 1"
line = 5
code = "code1"
character = 23
tool = "tidypy"

[[issues."subdir/foobar.json"]]
message = "Message 3"
line = 5
code = "code3"
character = 23
tool = "tidypy"

[[issues."blah/bar.py"]]
message = "Message 1"
line = 28
code = "code1"
character = 0
tool = "tidypy"

'''

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


def test_yaml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'yaml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''issues:
  blah/bar.py:
  - character: 0
    code: code1
    line: 28
    message: Message 1
    tool: tidypy
  foo.py:
  - character: 0
    code: code2
    line: 2
    message: Message 2
    tool: tidypy
  - character: 23
    code: code1
    line: 5
    message: Message 1
    tool: tidypy
  subdir/foobar.json:
  - character: 23
    code: code3
    line: 5
    message: Message 3
    tool: tidypy
tidypy: 0.1.0
'''

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


def test_csv_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'csv'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    expected = '''filename,line,character,tool,code,message
foo.py,2,0,tidypy,code2,Message 2
foo.py,5,23,tidypy,code1,Message 1
subdir/foobar.json,5,23,tidypy,code3,Message 3
blah/bar.py,28,0,tidypy,code1,Message 1
'''

    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''

