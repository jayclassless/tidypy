
import os.path
import stat
import subprocess  # noqa: bandit:B404
import sys

from ..config import get_project_config
from ..core import execute_tools
from ..reports.console import ConsoleReport
from ..util import read_file


HOOK_TEMPLATE = '''#!{executable}
# TIDYPY-INSTALLED-HOOK

import os.path
import sys

from tidypy.plugin import git

if __name__ == '__main__':
    project_path = os.path.normpath(os.path.join(
        os.path.abspath(__file__),
        '../../..',
    ))

    strict = git.git_config('--bool', '--get', 'tidypy.strict') == 'true'

    sys.exit(git.hook(project_path, strict))
'''


def git_config(*args):
    proc = subprocess.Popen(  # noqa: bandit:B603
        ['git', 'config'] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, _ = proc.communicate()
    return out.strip()


def hook(project_path, strict):
    cfg = get_project_config(project_path)
    collector = execute_tools(cfg, project_path)

    report = ConsoleReport(cfg, project_path)
    report.execute(collector)

    if strict and collector.issue_count() > 0:
        return 1

    return 0


class GitHook(object):
    def __init__(self):
        try:
            subprocess.call(['git'])  # noqa: bandit:B603,bandit:B607
        except OSError:
            self._git_available = False
        else:
            self._git_available = True

    def get_hook_dir(self, path, ensure_exists=False):
        git_dir = os.path.join(path, '.git')
        if not os.path.exists(git_dir):
            return None

        hook_dir = os.path.join(git_dir, 'hooks')
        if not os.path.exists(hook_dir):
            if ensure_exists:
                os.mkdir(hook_dir)
                return hook_dir
            return None
        return hook_dir

    def install(self, path, strict):
        hook_dir = self.get_hook_dir(path, ensure_exists=True)
        if not hook_dir:
            raise Exception(
                'Could not find Git configuration directory in: %s' % (
                    path,
                )
            )

        hook_filepath = os.path.join(hook_dir, 'pre-commit')
        if os.path.exists(hook_filepath):
            content = read_file(hook_filepath)
            if 'TIDYPY-INSTALLED-HOOK' not in content:
                raise Exception('A pre-commit hook already exists')

        executable = sys.executable or '/usr/bin/env python'

        with open(hook_filepath, 'w') as hook_file:
            hook_file.write(HOOK_TEMPLATE.format(
                executable=executable,
            ))

        os.chmod(hook_filepath, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

        if self._git_available:
            git_config('--add', 'tidypy.strict', str(strict).lower())

    def remove(self, path):
        hook_dir = self.get_hook_dir(path)
        if not hook_dir:
            return

        hook_filepath = os.path.join(hook_dir, 'pre-commit')
        if not os.path.exists(hook_filepath):
            return

        content = read_file(hook_filepath)
        if 'TIDYPY-INSTALLED-HOOK' not in content:
            raise Exception(
                "The pre-commit hook in place is not TidyPy's",
            )

        os.remove(hook_filepath)

        if self._git_available:
            git_config('--remove-section', 'tidypy')

