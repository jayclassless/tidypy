import random

from tidypy import Collector, Issue, TidyPyIssue, get_default_config


class FooIssue(Issue):
    tool = 'foo'

class BarIssue(Issue):
    tool = 'bar'


def test_basics():
    collector = Collector(get_default_config())
    assert collector.get_issues() == []
    assert len(collector.all_issues) == 0

    collector.add_issues(
        FooIssue('test', 'test message', 'test/file.ext', 1),
    )
    collector.add_issues([
        FooIssue('test2', 'test message 2', 'test/file.ext', 2),
        BarIssue('test3', 'test message 3', 'test/file.ext', 3),
    ])
    assert len(collector.all_issues) == 3


def test_disabled():
    cfg = get_default_config()
    cfg['disabled'] = ['foo']
    collector = Collector(cfg)

    collector.add_issues([
        TidyPyIssue('code1', 'message 1', 'test1.py', 2),
        TidyPyIssue('foo', 'message 2', 'test2.py', 3),
    ])

    assert len(collector.all_issues) == 1
    assert collector.all_issues[0].code == 'code1'


def test_sort_issues_default():
    collector = Collector(get_default_config())
    expected = [
        BarIssue('test', 'test message', 'test/file.ext', 2),
        BarIssue('test2', 'test message', 'test/file.ext', 2),
        FooIssue('test', 'test message', 'test/file.ext', 2),
        FooIssue('test2', 'test message', 'test/file.ext', 2),
        BarIssue('test', 'test message', 'test/file.ext', 2, 5),
        BarIssue('test2', 'test message', 'test/file.ext', 2, 5),
        FooIssue('test', 'test message', 'test/file.ext', 2, 5),
        FooIssue('test2', 'test message', 'test/file.ext', 2, 5),
        BarIssue('test', 'test message', 'test/file.ext', 5, 3),
        BarIssue('test2', 'test message', 'test/file.ext', 5, 3),
        FooIssue('test', 'test message', 'test/file.ext', 5, 3),
        FooIssue('test2', 'test message', 'test/file.ext', 5, 3),
        BarIssue('test', 'test message', 'test/file2.ext', 2),
        BarIssue('test2', 'test message', 'test/file2.ext', 2),
        FooIssue('test', 'test message', 'test/file2.ext', 2),
        FooIssue('test2', 'test message', 'test/file2.ext', 2),
        BarIssue('test', 'test message', 'test/file2.ext', 2, 5),
        BarIssue('test2', 'test message', 'test/file2.ext', 2, 5),
        FooIssue('test', 'test message', 'test/file2.ext', 2, 5),
        FooIssue('test2', 'test message', 'test/file2.ext', 2, 5),
        BarIssue('test', 'test message', 'test/file2.ext', 5, 3),
        BarIssue('test2', 'test message', 'test/file2.ext', 5, 3),
        FooIssue('test', 'test message', 'test/file2.ext', 5, 3),
        FooIssue('test2', 'test message', 'test/file2.ext', 5, 3),
    ]
    shuffled = [] + expected
    random.shuffle(shuffled)

    assert collector.sort_issues(shuffled) == expected


def test_sort_issues_custom():
    collector = Collector(get_default_config())
    expected = [
        BarIssue('test', 'test message', 'test/file.ext', 2),
        BarIssue('test2', 'test message', 'test/file.ext', 2),
        BarIssue('test2', 'test message', 'test/file.ext', 5),
        FooIssue('test', 'test message', 'test/file.ext', 2),
        FooIssue('test2', 'test message', 'test/file.ext', 2),
        FooIssue('test2', 'test message', 'test/file.ext', 5),
    ]
    shuffled = [] + expected
    random.shuffle(shuffled)

    assert collector.sort_issues(shuffled, ('tool', 'code', 'line')) == expected


def test_sort_issues_empty():
    collector = Collector(get_default_config())
    expected = [
        BarIssue('test', 'test message', 'test/file.ext', 2),
        BarIssue('test2', 'test message', 'test/file.ext', 2),
        BarIssue('test2', 'test message', 'test/file.ext', 5),
        FooIssue('test', 'test message', 'test/file.ext', 2),
        FooIssue('test2', 'test message', 'test/file.ext', 2),
        FooIssue('test2', 'test message', 'test/file.ext', 5),
    ]

    assert collector.sort_issues(expected, ()) == expected


def test_get_grouped_issues_default():
    cfg = get_default_config()
    cfg['merge_issues'] = False
    collector = Collector(cfg)
    expected = {
        'test/file.ext': [
            BarIssue('test', 'test message', 'test/file.ext', 2),
            BarIssue('test2', 'test message', 'test/file.ext', 2),
            FooIssue('test', 'test message', 'test/file.ext', 2),
            FooIssue('test2', 'test message', 'test/file.ext', 2),
            BarIssue('test', 'test message', 'test/file.ext', 2, 5),
            BarIssue('test2', 'test message', 'test/file.ext', 2, 5),
            FooIssue('test', 'test message', 'test/file.ext', 2, 5),
            FooIssue('test2', 'test message', 'test/file.ext', 2, 5),
            BarIssue('test', 'test message', 'test/file.ext', 5, 3),
            BarIssue('test2', 'test message', 'test/file.ext', 5, 3),
            FooIssue('test', 'test message', 'test/file.ext', 5, 3),
            FooIssue('test2', 'test message', 'test/file.ext', 5, 3),
        ],
        'test/file2.ext': [
            BarIssue('test', 'test message', 'test/file2.ext', 2),
            BarIssue('test2', 'test message', 'test/file2.ext', 2),
            FooIssue('test', 'test message', 'test/file2.ext', 2),
            FooIssue('test2', 'test message', 'test/file2.ext', 2),
            BarIssue('test', 'test message', 'test/file2.ext', 2, 5),
            BarIssue('test2', 'test message', 'test/file2.ext', 2, 5),
            FooIssue('test', 'test message', 'test/file2.ext', 2, 5),
            FooIssue('test2', 'test message', 'test/file2.ext', 2, 5),
            BarIssue('test', 'test message', 'test/file2.ext', 5, 3),
            BarIssue('test2', 'test message', 'test/file2.ext', 5, 3),
            FooIssue('test', 'test message', 'test/file2.ext', 5, 3),
            FooIssue('test2', 'test message', 'test/file2.ext', 5, 3),
        ],
    }

    shuffled = []
    for issues in expected.values():
        shuffled += issues
    random.shuffle(shuffled)

    collector.add_issues(shuffled)

    assert collector.get_grouped_issues() == expected


def test_get_grouped_issues_custom():
    collector = Collector(get_default_config())
    expected = {
        'test': [
            BarIssue('test', 'test message', 'test/file.ext', 2),
            FooIssue('test', 'test message', 'test/file.ext', 2),
        ],
        'test2': [
            BarIssue('test2', 'test message', 'test/file.ext', 2),
            BarIssue('test2', 'test message', 'test/file.ext', 5),
            FooIssue('test2', 'test message', 'test/file.ext', 2),
            FooIssue('test2', 'test message', 'test/file.ext', 5),
        ],
    }

    shuffled = []
    for issues in expected.values():
        shuffled += issues
    random.shuffle(shuffled)

    collector.add_issues(shuffled)

    assert collector.get_grouped_issues(lambda x: x.code, ('tool', 'line')) == expected


def test_disabled():
    cfg = get_default_config()
    cfg['disabled'] = ['test']
    collector = Collector(cfg)
    issues = [
        TidyPyIssue('test', 'test message', 'test/file.ext', 2),
        TidyPyIssue('test2', 'test message', 'test/file.ext', 2),
        TidyPyIssue('test3', 'test message', 'test/file.ext', 2),

    ]
    collector.add_issues(issues)

    assert collector.get_issues() == issues[1:]


def test_merging_dupes():
    collector = Collector(get_default_config())
    issues = [
        TidyPyIssue('test', 'test message', 'test/file.ext', 2),
        TidyPyIssue('test', 'test message', 'test/file.ext', 2),
        TidyPyIssue('test2', 'test message', 'test/file.ext', 2),
        TidyPyIssue('test', 'test message', 'test/file.ext', 3),
        TidyPyIssue('test2', 'test message', 'test/file2.ext', 2),

    ]
    collector.add_issues(issues)

    assert collector.get_issues() == [issues[0]] + issues[2:]

