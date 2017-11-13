from __future__ import absolute_import

import os
import sys

from setuptools import Command

from ..config import get_project_config
from ..core import execute_tools, execute_reports


class TidyPyCommand(Command):
    description = 'Executes TidyPy on the project and shows the results.'

    user_options = [
        (
            'project-path=',
            'p',
            'The path to the base of the project to analyze with TidyPy.',
        ),
        (
            'fail-on-issue',
            'f',
            'Whether or not the command should fail if TidyPy finds issues.',
        ),
    ]

    boolean_options = [
        'fail-on-issue',
    ]

    def initialize_options(self):
        # pylint: disable=attribute-defined-outside-init
        self.project_path = os.getcwd()
        self.fail_on_issue = False

    def finalize_options(self):
        pass

    def run(self):
        cfg = get_project_config(self.project_path)
        collector = execute_tools(cfg, self.project_path)
        execute_reports(cfg, self.project_path, collector)

        if self.fail_on_issue and collector.issue_count() > 0:
            sys.exit(1)

