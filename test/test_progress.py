
from tidypy import get_default_config, get_tools
from tidypy.progress import QuietProgress, ConsoleProgress


def test_console_progress(capsys):
    cfg = get_default_config()
    for tool in get_tools():
        cfg[tool]['use'] = tool in ('pylint', 'pycodestyle')

    progress = ConsoleProgress(cfg)
    progress.on_start()

    progress.on_tool_start('pylint')
    assert progress.current_tools == ['pylint']
    assert progress.completed_tools == []
    assert progress.currently_executing == '[pylint]'

    progress.on_tool_start('pycodestyle')
    assert progress.current_tools == ['pylint', 'pycodestyle']
    assert progress.completed_tools == []
    assert progress.currently_executing == '[pylint, pycodestyle]'

    progress.on_tool_finish('pycodestyle')
    progress.on_tool_finish('pycodestyle')
    assert progress.current_tools == ['pylint']
    assert progress.completed_tools == ['pycodestyle']
    assert progress.currently_executing == '[pylint]'

    progress.on_tool_finish('pylint')
    assert progress.current_tools == []
    assert progress.completed_tools == ['pycodestyle', 'pylint']
    assert progress.currently_executing == ''

    progress.on_finish()


def test_quiet_progress(capsys):
    cfg = get_default_config()
    for tool in get_tools():
        cfg[tool]['use'] = tool in ('pylint', 'pycodestyle')

    progress = QuietProgress()
    progress.on_start()

    progress.on_tool_start('pylint')
    assert progress.current_tools == ['pylint']
    assert progress.completed_tools == []

    progress.on_tool_start('pycodestyle')
    assert progress.current_tools == ['pylint', 'pycodestyle']
    assert progress.completed_tools == []

    progress.on_tool_finish('pycodestyle')
    assert progress.current_tools == ['pylint']
    assert progress.completed_tools == ['pycodestyle']

    progress.on_tool_finish('pylint')
    assert progress.current_tools == []
    assert progress.completed_tools == ['pycodestyle', 'pylint']

    progress.on_finish()
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

