
import logging
import os
import warnings

from ..util import SysOutCapture
from .base import Tool, Issue, ToolIssue


# Hacks to prevent pyroma from screwing up the logging system for everyone else
old_config = logging.basicConfig
try:
    logging.basicConfig = lambda **k: None
    from pyroma import projectdata, ratings
finally:
    logging.basicConfig = old_config


# Hacks so we can get the messages of these tests without running them.
HACKS = (
    ('PythonVersion', '_major_version_specified', False),
    ('ValidREST', '_message', ''),
    ('ClassifierVerification', '_incorrect', []),
    ('Licensing', '_message', ''),
)
for clazz, attr, value in HACKS:
    if hasattr(ratings, clazz):
        setattr(getattr(ratings, clazz), attr, value)


TIDYPY_ISSUES = {
    'NOT_CALLED': (
        'SetupNotCalled',
        'setup() was not invoked.',
    ),

    'SCRIPT_FAIL': (
        'SetupFailed',
        'Execution of the setup module failed:\n%s',
    ),

    'RST_ERROR': (
        'RstProblem',
        'The reStructuredText in your description generated errors:\n%s',
    ),
}


class PyromaIssue(Issue):
    tool = 'pyroma'


class PyromaTool(Tool):
    """
    Pyroma tests your project's packaging friendliness.
    """

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
            (test.__class__.__name__, test.message().strip())
            for test in ratings.ALL_TESTS
        ] + list(TIDYPY_ISSUES.values())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled = self.config['disabled'][:]
        if 'LicenseClassifier' in self.disabled:
            self.disabled.append('LicenceClassifier')
        if 'Licence' in self.disabled:
            self.disabled.append('License')

    def execute(self, finder):
        issues = []

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
                        if name in self.disabled:
                            continue

                        if test.test(data) is False:
                            issues.append(PyromaIssue(
                                name,
                                test.message(),
                                filepath,
                            ))

                    err = capture.get_stderr()
                    if err:
                        if err.startswith('<string>:'):
                            issues.append(PyromaIssue(
                                TIDYPY_ISSUES['RST_ERROR'][0],
                                TIDYPY_ISSUES['RST_ERROR'][1] % (err,),
                                filepath,
                            ))
                        else:
                            issues.append(ToolIssue(
                                err,
                                filepath,
                            ))

        return [
            issue
            for issue in issues
            if issue.code not in self.disabled
        ]

