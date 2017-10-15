
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
)
from .progress import TidyBar
from .util import output_error, render_toml, render_json, render_yaml


# pylint: disable=too-many-arguments


@click.group(
    help='A tool that executes several static analysis tools upon a Python'
    ' project and aggregates the results.',
)
@click.version_option()
def main():
    pass


@main.command(
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
    '--no-merge',
    is_flag=True,
    help='Disable the merging of issues from various tools when TidyPy'
    ' considers them equivalent. Overrides the configuration file.',
)
@click.option(
    '--silence-tools',
    is_flag=True,
    help='If the execution of a tool results in an unexpected output or '
    ' Exception, be quiet about it. The default behavior is to capture the'
    ' information as an issue.',
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
    '--no-progress',
    is_flag=True,
    help='Disable the display of the progress bar.',
)
@click.argument(
    'path',
    type=click.Path(exists=True),
    default=os.getcwd(),
)
def check(
        excludes,
        tools,
        reports,
        no_merge,
        silence_tools,
        threads,
        no_progress,
        path):
    # Clean up the path
    path = os.path.abspath(path)

    # Establish the configuration
    try:
        config = get_project_config(path)
    except Exception as exc:  # pylint: disable=broad-except
        output_error('Could not parse config file: %s' % (exc,))
        return

    if excludes:
        config['exclude'] = excludes
    if no_merge:
        config['merge_issues'] = False
    if silence_tools:
        config['silence_tools'] = True
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

    progress = TidyBar(config, quiet=no_progress)
    collector = execute_tools(
        config,
        path,
        on_tool_start=progress.on_tool_start,
        on_tool_finish=progress.on_tool_finish,
    )
    progress.finish()

    execute_reports(config, path, collector)


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

