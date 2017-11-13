
import csv
import os

from collections import OrderedDict

import click

from six import iteritems

from .core import execute_tools, execute_reports
from .config import (
    get_tools,
    get_reports,
    get_default_config,
    get_project_config,
    purge_config_cache,
)
from .plugin.git import GitHook
from .plugin.mercurial import MercurialHook
from .progress import QuietProgress, ConsoleProgress
from .util import output_error, render_toml, render_json, render_yaml


# pylint: disable=too-many-arguments


@click.group(
    help='A tool that executes several static analysis tools upon a Python'
    ' project and aggregates the results.',
)
@click.version_option()
def main():
    pass


@main.command(  # noqa
    'check',
    short_help='Executes the tools upon the project files.',
    help='''Executes the tools upon the project files.

Accepts one argument, which is the path to the base of the Python project.
If not specified, defaults to the current working directory.
''',
)
@click.option(
    '--exclude',
    '-x',
    'excludes',
    multiple=True,
    metavar='REGEX',
    help='Specifies a regular expression matched against paths that you want'
    ' to exclude from the examination. Can be specified multiple times.'
    ' Overrides the expressions specified in the configuration file.',
)
@click.option(
    '--tool',
    '-t',
    'tools',
    multiple=True,
    type=click.Choice(sorted([
        name
        for name, cls in iteritems(get_tools())
        if cls.can_be_used()
    ])),
    help='Specifies the name of a tool to use during the examination. Can be'
    ' specified multiple times. Overrides the configuration file.',
)
@click.option(
    '--report',
    '-r',
    'reports',
    multiple=True,
    type=click.Choice(sorted(get_reports().keys())),
    help='Specifies the name of a report to execute after the examination. Can'
    ' be specified multiple times. Overrides the configuration file.',
)
@click.option(
    '--disable-merge',
    is_flag=True,
    help='Disable the merging of issues from various tools when TidyPy'
    ' considers them equivalent. Overrides the configuration file.',
)
@click.option(
    '--threads',
    type=click.IntRange(1),
    default=3,
    show_default=True,
    metavar='NUM_THREADS',
    help='The number of threads to use to concurrently execute the tools.'
    ' Overrides the configuration file.',
)
@click.option(
    '--disable-progress',
    is_flag=True,
    help='Disable the display of the progress bar.',
)
@click.option(
    '--disable-noqa',
    is_flag=True,
    help='Disable the ability to ignore issues using the "# noqa" comment in'
    ' Python files.',
)
@click.option(
    '--disable-config-cache',
    is_flag=True,
    help='Disable the use of the cache when retrieving configurations'
    ' referenced by the "extends" option.',
)
@click.argument(
    'path',
    type=click.Path(exists=True),
    default=os.getcwd(),
)
@click.pass_context
def check(
        ctx,
        excludes,
        tools,
        reports,
        disable_merge,
        threads,
        disable_progress,
        disable_noqa,
        disable_config_cache,
        path):
    # Clean up the path
    path = os.path.abspath(path)

    # Establish the configuration
    try:
        config = get_project_config(path, use_cache=not disable_config_cache)
    except Exception as exc:  # pylint: disable=broad-except
        output_error('Could not parse config file: %s' % (exc,))
        ctx.exit(1)

    if excludes:
        config['exclude'] = excludes
    if disable_merge:
        config['merge-issues'] = False
    if disable_noqa:
        config['noqa'] = False
    if threads:
        config['threads'] = threads
    if tools:
        for tool in get_tools():
            config[tool]['use'] = tool in tools
    if reports:
        config['reports'] = [
            {'type': report}
            for report in reports
        ]

    if disable_progress:
        progress = QuietProgress()
    else:
        progress = ConsoleProgress(config)

    collector = execute_tools(
        config,
        path,
        progress=progress,
    )

    if collector.failure:
        ctx.exit(1)

    execute_reports(config, path, collector)

    if collector.get_issues():
        ctx.exit(1)


@main.command(
    'list-codes',
    short_help='Outputs a listing of all known issue codes that tools may'
    ' report.',
    help='Outputs a listing of all known issue codes that tools may report.',
)
@click.option(
    '--tool',
    '-t',
    'tools',
    multiple=True,
    type=click.Choice(sorted(get_tools().keys())),
    help='Specifies the name of a tool whose codes should be output. If not'
    ' specified, defaults to all tools.',
)
@click.option(
    '--format',
    '-f',
    'fmt',
    type=click.Choice(['toml', 'json', 'yaml', 'csv']),
    default='toml',
    help='Specifies the format in which the tools should be output. If not'
    ' specified, defaults to TOML.',
)
def list_codes(tools, fmt):
    all_tools = get_tools()
    tools = tools or sorted(all_tools.keys())
    codes = OrderedDict()

    for tool in tools:
        codes[tool] = dict(all_tools[tool].get_all_codes())

    if fmt == 'toml':
        click.echo(render_toml(codes))
    elif fmt == 'json':
        click.echo(render_json(codes))
    elif fmt == 'yaml':
        click.echo(render_yaml(codes))
    elif fmt == 'csv':
        writer = csv.writer(click.get_text_stream('stdout'))
        writer.writerow(['tool', 'code', 'message'])
        for tool in codes:
            for code, message in iteritems(codes[tool]):
                writer.writerow([tool, code, message])


@main.command(
    'default-config',
    short_help='Outputs a default configuration that can be used to bootstrap'
    ' your own configuration file.',
    help='Outputs a default configuration that can be used to bootstrap'
    ' your own configuration file.',
)
@click.option(
    '--pyproject',
    is_flag=True,
    help='Output the config so that it can be used in a pyproject.toml file.',
)
def default_config(pyproject):
    config = get_default_config()

    # Don't include empty option dicts
    for tool in get_tools():
        if not config[tool]['options']:
            del config[tool]['options']

    if pyproject:
        config = {'tool': {'tidypy': config}}

    click.echo(render_toml(config))


@main.command(
    'purge-config-cache',
    short_help='Deletes the cache of configurations retrieved from outside the'
    ' primary configuration.',
    help='Deletes the cache of configurations retrieved from outside the'
    ' primary configuration.',
)
def purge_cache():
    purge_config_cache()


@main.command(
    'install-vcs',
    short_help='Installs TidyPy as a pre-commit hook into the specified VCS.',
    help='''Installs TidyPy as a pre-commit hook into the specified VCS.

Accepts two arguments:

  VCS: The version control system to install the hook into. Choose from: git,
hg

  PATH: The path to the base of the repository to install the hook into. If not
specified, defaults to the current working directory.
''',
)
@click.option(
    '--strict',
    is_flag=True,
    help='Whether or not the hook should prevent the commit if TidyPy finds'
    ' issues.',
)
@click.argument(
    'vcs',
    type=click.Choice(['git', 'hg']),
)
@click.argument(
    'path',
    type=click.Path(exists=True),
    default=os.getcwd(),
)
@click.pass_context
def install_vcs(ctx, vcs, path, strict):
    if vcs == 'hg':
        hook = MercurialHook()
    elif vcs == 'git':
        hook = GitHook()

    try:
        hook.install(path, strict)
    except Exception as exc:  # pylint: disable=broad-except
        output_error('VCS hook installation failed: %s' % (exc,))
        ctx.exit(1)


@main.command(
    'remove-vcs',
    short_help='Removes the TidyPy pre-commit hook from the specified VCS.',
    help='''Removes the TidyPy pre-commit hook from the specified VCS.

Accepts two arguments:

  VCS: The version control system to remove the hook from. Choose from: git,
hg

  PATH: The path to the base of the repository to remove the hook from. If not
specified, defaults to the current working directory.
''',
)
@click.argument(
    'vcs',
    type=click.Choice(['git', 'hg']),
)
@click.argument(
    'path',
    type=click.Path(exists=True),
    default=os.getcwd(),
)
@click.pass_context
def remove_vcs(ctx, vcs, path):
    if vcs == 'hg':
        hook = MercurialHook()
    elif vcs == 'git':
        hook = GitHook()

    try:
        hook.remove(path)
    except Exception as exc:  # pylint: disable=broad-except
        output_error('VCS hook removal failed: %s' % (exc,))
        ctx.exit(1)

