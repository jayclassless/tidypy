
import sys
import subprocess

import pytest


@pytest.mark.skipif(sys.platform == 'win32', reason='windows hates setuptools')
def test_default():
    proc = subprocess.Popen(
        ['python', 'setup.py', 'tidypy'],
        cwd='test/project1',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    out, err = proc.communicate()
    assert out.startswith('running tidypy')
    assert proc.returncode == 0


@pytest.mark.skipif(sys.platform == 'win32', reason='windows hates setuptools')
def test_options():
    proc = subprocess.Popen(
        ['python', 'setup.py', 'tidypy', '--fail-on-issue', '--project-path=test/project1'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    out, err = proc.communicate()
    assert out.startswith('running tidypy')
    assert proc.returncode == 1

