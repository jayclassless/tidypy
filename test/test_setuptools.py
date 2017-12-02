
import subprocess


def test_default():
    proc = subprocess.Popen(
        ['python', 'setup.py', 'tidypy'],
        cwd='test/project1',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate()
    assert out.startswith('running tidypy')
    assert proc.returncode == 0


def test_options():
    proc = subprocess.Popen(
        ['python', 'setup.py', 'tidypy', '--fail-on-issue', '--project-path=test/project1'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate()
    assert out.startswith('running tidypy')
    assert proc.returncode == 1

