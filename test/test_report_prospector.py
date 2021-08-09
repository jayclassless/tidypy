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
  "summary": {
    "started": "2021-08-09 16:27:54.695977",
    "libraries": [],
    "strictness": "from profile",
    "profiles": "tidypy",
    "tools": [
      "bandit",
      "dlint",
      "eradicate",
      "jsonlint",
      "manifest",
      "mccabe",
      "polint",
      "pycodestyle",
      "pydiatra",
      "pydocstyle",
      "pyflakes",
      "pylint",
      "pyroma",
      "rstlint",
      "secrets",
      "vulture",
      "yamllint"
    ],
    "message_count": 4,
    "completed": "2021-08-09 16:27:54.695977",
    "time_taken": "0",
    "formatter": "json"
  },
  "messages": [
    {
      "source": "tidypy",
      "code": "code1",
      "location": {
        "path": "blah/bar.py",
        "module": null,
        "function": null,
        "line": 28,
        "character": 0
      },
      "message": "Message 1"
    },
    {
      "source": "tidypy",
      "code": "code2",
      "location": {
        "path": "foo.py",
        "module": null,
        "function": null,
        "line": 2,
        "character": 0
      },
      "message": "Message 2"
    },
    {
      "source": "tidypy",
      "code": "code1",
      "location": {
        "path": "foo.py",
        "module": null,
        "function": null,
        "line": 5,
        "character": 23
      },
      "message": "Message 1"
    },
    {
      "source": "tidypy",
      "code": "code3",
      "location": {
        "path": "subdir/foobar.json",
        "module": null,
        "function": null,
        "line": 5,
        "character": 23
      },
      "message": "Message 3"
    }
  ]
}
'''


def test_json_execute(capsys):
    cfg = get_default_config()
    cfg['requested_reports'] = [{'type': 'prospector-json'}]

    collector = Collector(cfg)
    collector.add_issues(ISSUES)

    execute_reports(cfg, 'someproject', collector)

    out, err = capsys.readouterr()
    
    assert EXPECTED_JSON == out.replace('\r\n', '\n')
    assert err == ''
