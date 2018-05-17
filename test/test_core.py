
import six

from tidypy import execute_tools, execute_reports, get_default_config, \
    get_tools, Collector, QuietProgress


def test_execute_tools(capsys):
    cfg = get_default_config()
    cfg['pycodestyle']['use'] = False

    expected_tools = sorted(get_tools())
    expected_tools.remove('pycodestyle')
    if six.PY3:
        expected_tools.remove('eradicate')
        expected_tools.remove('2to3')

    progress = QuietProgress()
    collector = execute_tools(cfg, 'test/project1', progress=progress)
    assert isinstance(collector, Collector)
    assert [] == sorted(progress.current_tools)
    assert expected_tools == sorted(progress.completed_tools)

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


    for tool in get_tools():
        cfg[tool]['use'] = False

    progress = QuietProgress()
    collector = execute_tools(cfg, 'test/project1', progress=progress)
    assert isinstance(collector, Collector)
    assert [] == sorted(progress.current_tools)
    assert [] == sorted(progress.completed_tools)
    assert collector.issue_count() == 0
    assert collector.issue_count(include_unclean=True) == 0

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


def test_execute_reports(capsys):
    cfg = get_default_config()
    cfg['reports'] = [
        {'type': 'null'},
        {'type': 'doesntexist'},
    ]
    collector = execute_tools(cfg, 'test/project1')

    executed = []
    def on_finish(report):
        executed.append(report['type'])

    execute_reports(cfg, 'test/project1', collector, on_report_finish=on_finish)
    assert ['null'] == sorted(executed)

    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

