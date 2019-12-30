
from pathlib import Path

from .base import Extender, DoesNotExistError


class FilesysExtender(Extender):
    @classmethod
    def can_handle(cls, location):
        return True

    @classmethod
    def retrieve(cls, location, project_path):
        path = Path(location)
        if not path.is_absolute():
            path = Path(project_path).joinpath(path)
        if not path.exists():
            raise DoesNotExistError()

        with path.open('r') as config_file:
            content = config_file.read()

        return cls.parse(
            content,
            is_pyproject=path.parts[-1] == 'pyproject.toml',
        )

