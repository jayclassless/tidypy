
from tidypy import get_default_config, get_tools
from tidypy.progress import TidyBar


def test_progress(capsys):
    cfg = get_default_config()
    for tool in get_tools():
        cfg[tool]['use'] = tool in ('pylint', 'pycodestyle')

    bar = TidyBar(cfg)

    bar.on_tool_start('pylint')
    assert bar.progress == 0
    assert bar.currently_executing == '[pylint]'

    bar.on_tool_start('pycodestyle')
    assert bar.progress == 0
    assert bar.currently_executing == '[pylint, pycodestyle]'

    bar.on_tool_finish('pycodestyle')
    bar.on_tool_finish('pycodestyle')
    assert bar.progress == 0.5
    assert bar.currently_executing == '[pylint]'

    bar.on_tool_finish('pylint')
    assert bar.progress == 1.0
    assert bar.currently_executing == ''

    bar.finish()


def test_progress_quiet(capsys):
    cfg = get_default_config()
    for tool in get_tools():
        cfg[tool]['use'] = tool in ('pylint', 'pycodestyle')

    bar = TidyBar(cfg, quiet=True)

    bar.on_tool_start('pylint')
    assert bar.progress == 0
    assert bar.currently_executing == ''

    bar.on_tool_start('pycodestyle')
    assert bar.progress == 0
    assert bar.currently_executing == ''

    bar.on_tool_finish('pycodestyle')
    assert bar.progress == 0
    assert bar.currently_executing == ''

    bar.on_tool_finish('pylint')
    assert bar.progress == 0
    assert bar.currently_executing == ''

    bar.finish()
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

