from __future__ import absolute_import

import logging
import os
import warnings

from ..util import SysOutCapture
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


TIDYPY_ISSUES = {
    'NOT_CALLED': (
        'SetupNotCalled',
        'setup() was not invoked.',
    ),

    'SCRIPT_FAIL': (
        'SetupFailed',
        'Execution of the setup module failed:\n%s',
    ),
}


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
        ] + list(TIDYPY_ISSUES.values())

    def execute(self, finder):
        issues = []

        disabled = self.config['disabled'][:]
        if 'LicenseClassifier' in disabled:
            disabled.append('LicenceClassifier')
        if 'Licence' in disabled:
            disabled.append('License')

        for filepath in finder.files(self.config['filters']):
            dirname, _ = os.path.split(filepath)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                with SysOutCapture() as capture:
                    try:
                        data = projectdata.get_data(dirname)
                    except RuntimeError:
                        err = capture.get_stderr()
                        if err:
                            issues.append(PyromaIssue(
                                TIDYPY_ISSUES['SCRIPT_FAIL'][0],
                                TIDYPY_ISSUES['SCRIPT_FAIL'][1] % (err,),
                                filepath,
                            ))
                        else:
                            issues.append(PyromaIssue(
                                TIDYPY_ISSUES['NOT_CALLED'][0],
                                TIDYPY_ISSUES['NOT_CALLED'][1],
                                filepath,
                            ))
                        continue

            for test in ratings.ALL_TESTS:
                name = test.__class__.__name__
                if name in disabled:
                    continue

                if test.test(data) is False:
                    issues.append(PyromaIssue(
                        name,
                        test.message(),
                        filepath,
                    ))

        return issues

