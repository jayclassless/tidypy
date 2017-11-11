
from click.testing import CliRunner

from tidypy.cli import main


def test_default():
    runner = CliRunner()

    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert result.output != ''

    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert result.output != ''


def test_check():
    runner = CliRunner()

    result = runner.invoke(main, ['check', 'test/project1'])
    assert result.exit_code == 1
    assert result.output != ''

    result = runner.invoke(main, ['check', 'test/project1', '--exclude=blahblah', '--disable-merge', '--disable-noqa', '--threads=4', '--tool=pylint', '--disable-progress', '--report=null'])
    assert result.exit_code == 1
    assert result.output == ''


def test_list_codes():
    runner = CliRunner()

    result = runner.invoke(main, ['list-codes'])
    assert result.exit_code == 0
    assert result.output != ''

    toml_result = runner.invoke(main, ['list-codes', '--format=toml'])
    assert toml_result.exit_code == 0
    assert toml_result.output != ''

    json_result = runner.invoke(main, ['list-codes', '--format=json'])
    assert json_result.exit_code == 0
    assert json_result.output != ''
    assert json_result.output != toml_result.output

    yaml_result = runner.invoke(main, ['list-codes', '--format=yaml'])
    assert yaml_result.exit_code == 0
    assert yaml_result.output != ''
    assert yaml_result.output != toml_result.output
    assert yaml_result.output != json_result.output

    csv_result = runner.invoke(main, ['list-codes', '--format=csv'])
    assert csv_result.exit_code == 0
    assert csv_result.output != ''
    assert csv_result.output != toml_result.output
    assert csv_result.output != json_result.output
    assert csv_result.output != yaml_result.output


def test_default_config():
    runner = CliRunner()

    result = runner.invoke(main, ['default-config'])
    assert result.exit_code == 0
    assert result.output != ''

    result2 = runner.invoke(main, ['default-config', '--pyproject'])
    assert result2.exit_code == 0
    assert result2.output != ''
    assert result2.output != result.output


def test_purge_config_cache():
    runner = CliRunner()

    result = runner.invoke(main, ['purge-config-cache'])
    assert result.exit_code == 0

