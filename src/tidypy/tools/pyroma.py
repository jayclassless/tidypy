from __future__ import absolute_import

import logging
import os
import warnings

from .base import Tool, Issue


# Hacks to prevent pyroma from screwing up the logging system for everyone else
old_config = logging.basicConfig  # pylint: disable=invalid-name
try:
    logging.basicConfig = lambda **k: None
    from pyroma import projectdata, ratings
except ImportError:
    raise
finally:
    logging.basicConfig = old_config


# Hacks so we can get the messages of these tests without running them.
# pylint: disable=protected-access
ratings.PythonVersion._major_version_specified = False
ratings.ValidREST._message = ''


class PyromaIssue(Issue):
    tool = 'pyroma'


class PyromaTool(Tool):
    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'setup\.py$',
        ]
        return config

    @classmethod
    def get_all_codes(cls):
        return [
            (test.__class__.__name__, test.message())
            for test in ratings.ALL_TESTS
        ]

    def execute(self, finder):
        issues = []

        for filepath in finder.files(self.config['filters']):
            dirname, _ = os.path.split(filepath)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                data = projectdata.get_data(dirname)

            for test in ratings.ALL_TESTS:
                name = test.__class__.__name__
                if name in self.config['disabled']:
                    continue

                if test.test(data) is False:
                    issues.append(PyromaIssue(
                        name,
                        test.message(),
                        filepath,
                    ))

        return issues

