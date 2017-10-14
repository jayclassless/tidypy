
from tidypy import execute_tools, execute_reports, get_default_config, \
    get_tools, Collector


def test_execute_tools(capsys):
    cfg = get_default_config()

    started = []
    def on_start(tool):
        started.append(tool)
    finished = []
    def on_finish(tool):
        finished.append(tool)

    collector = execute_tools(cfg, 'test/project1', on_tool_start=on_start, on_tool_finish=on_finish)
    assert isinstance(collector, Collector)
    assert sorted(get_tools()) == sorted(started)
    assert sorted(get_tools()) == sorted(finished)

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

