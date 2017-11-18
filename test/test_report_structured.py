
import sys

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


EXPECTED_JSON = '''{
  "tidypy": "0.4.0",
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


def test_json_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'json'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert EXPECTED_JSON == out.replace('\r\n', '\n')
    assert err == ''


EXPECTED_TOML = '''tidypy = "0.4.0"

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


def test_toml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'toml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert EXPECTED_TOML == out.replace('\r\n', '\n')
    assert err == ''


EXPECTED_YAML = '''tidypy: 0.4.0
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


def test_yaml_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'yaml'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert EXPECTED_YAML == out.replace('\r\n', '\n')
    assert err == ''


EXPECTED_CSV = '''filename,line,character,tool,code,message
blah/bar.py,28,0,tidypy,code1,Message 1
foo.py,2,0,tidypy,code2,Message 2
foo.py,5,23,tidypy,code1,Message 1
subdir/foobar.json,5,23,tidypy,code3,Message 3
'''

def test_csv_execute(capsys):
    cfg = get_default_config()
    cfg['reports'] = [{'type': 'csv'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert EXPECTED_CSV == out.replace('\r\n', '\n')
    assert err == ''


def test_csv_file_output(capsys, tmpdir):
    target_dir = tmpdir.mkdir('reports')

    cfg = get_default_config()
    cfg['reports'] = [{'type': 'csv'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    test_file = str(target_dir) + 'test1'
    with open(test_file, 'w') as fp:
        execute_reports(cfg, 'someproject', collector, output_file=fp)

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

    assert EXPECTED_CSV == open(test_file, 'r').read()

    test_file = str(target_dir) + 'test2'
    cfg['reports'] = [{'type': 'csv', 'file': test_file}]
    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

    assert EXPECTED_CSV == open(test_file, 'r').read()

