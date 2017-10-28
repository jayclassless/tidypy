
import pytoml


class Extender(object):
    @classmethod
    def can_handle(cls, location):
        raise NotImplementedError()

    @classmethod
    def retrieve(cls, location, project_path):
        raise NotImplementedError()

    @classmethod
    def parse(cls, content, is_pyproject=False):
        parsed = pytoml.loads(content)

        if is_pyproject:
            parsed = parsed.get('tool', {})
        parsed = parsed.get('tidypy', {})

        return parsed


class ExtenderError(Exception):
    pass


class DoesNotExistError(ExtenderError):
    pass

