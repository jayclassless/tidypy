
import pytest

from tidypy import DoesNotExistError
from tidypy.extenders.filesys import FilesysExtender


def test_can_handle():
    assert FilesysExtender.can_handle('/foo/bar/tidypy') == True
    assert FilesysExtender.can_handle('/baz/pyproject.toml') == True


def test_retrieve(tmpdir):
    target_dir = tmpdir.mkdir('filesys')

    regular = target_dir.join('tidypy')
    regular.write("[tidypy]\ntest = 'foo'")
    pyproject = target_dir.join('pyproject.toml')
    pyproject.write("[tool.tidypy]\ntest = 'bar'")

    actual = FilesysExtender.retrieve(str(regular), 'test')
    assert actual['test'] == 'foo'

    actual = FilesysExtender.retrieve(str(pyproject.relto(target_dir)), str(target_dir))
    assert actual['test'] == 'bar'


def test_retrieve_missing(tmpdir):
    target_dir = tmpdir.mkdir('filesys')

    with pytest.raises(DoesNotExistError):
        actual = FilesysExtender.retrieve(str(target_dir) + 'doesntexist', 'test')

