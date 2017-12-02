
import subprocess

import pytest

from click.testing import CliRunner
from six import text_type

from tidypy.cli import main


def test_default():
    runner = CliRunner()

    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert result.output != ''

    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert result.output != ''


def test_check(tmpdir):
    runner = CliRunner()

    project_dir = tmpdir.mkdir('empty_project')
    result = runner.invoke(main, ['check', text_type(project_dir), '--disable-progress', '--report=null'])
    assert result.exit_code == 0
    assert result.output == ''

    result = runner.invoke(main, ['check', 'test/project1'])
    assert result.exit_code == 1
    assert result.output != ''

    result = runner.invoke(main, ['check', 'test/project1', '--exclude=blahblah', '--disable-merge', '--disable-noqa', '--workers=3', '--tool=pylint', '--disable-progress', '--report=null'])
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


def test_broken_config(tmpdir):
    runner = CliRunner()

    project_dir = tmpdir.mkdir('broken_project')
    project_dir.join('pyproject.toml').write('broken[garbage')

    result = runner.invoke(main, ['check', text_type(project_dir)])
    assert result.exit_code == 1
    assert result.output.startswith('Could not parse config file')


def test_purge_config_cache():
    runner = CliRunner()

    result = runner.invoke(main, ['purge-config-cache'])
    assert result.exit_code == 0


def executable_exists(executable):
    try:
        subprocess.call([executable])
    except OSError:
        return False
    else:
        return True


@pytest.mark.skipif(not executable_exists('git'), reason='git not available')
def test_vcs_git(tmpdir):
    git_dir = text_type(tmpdir.mkdir('git'))
    subprocess.call(['git', 'init', git_dir])

    runner = CliRunner()

    result = runner.invoke(main, ['install-vcs', 'git', git_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['install-vcs', 'git', git_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['remove-vcs', 'git', git_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['remove-vcs', 'git', git_dir])
    assert result.exit_code == 0

    other_dir = text_type(tmpdir.mkdir('other'))

    result = runner.invoke(main, ['install-vcs', 'git', other_dir])
    assert result.exit_code == 1

    result = runner.invoke(main, ['remove-vcs', 'git', other_dir])
    assert result.exit_code == 0


@pytest.mark.skipif(not executable_exists('hg'), reason='hg not available')
def test_vcs_mercurial(tmpdir):
    hg_dir = text_type(tmpdir.mkdir('mercurial'))
    subprocess.call(['hg', 'init', hg_dir])

    runner = CliRunner()

    result = runner.invoke(main, ['install-vcs', 'hg', hg_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['install-vcs', 'hg', hg_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['remove-vcs', 'hg', hg_dir])
    assert result.exit_code == 0

    result = runner.invoke(main, ['remove-vcs', 'hg', hg_dir])
    assert result.exit_code == 0

    other_dir = text_type(tmpdir.mkdir('other'))

    result = runner.invoke(main, ['install-vcs', 'hg', other_dir])
    assert result.exit_code == 1

    result = runner.invoke(main, ['remove-vcs', 'hg', other_dir])
    assert result.exit_code == 1

