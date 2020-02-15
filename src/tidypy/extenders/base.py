
import toml


class Extender(object):
    """
    The base class for TidyPy configuration extenders.
    """

    @classmethod
    def can_handle(cls, location):
        """
        Indicates whether or not this Extender is capable of retrieving the
        specified location.

        :param location:
            a URI indicating where to retrieve the TidyPy configuration from
        :type location: str
        :rtype: bool
        """

        raise NotImplementedError()

    @classmethod
    def retrieve(cls, location, project_path):
        """
        Retrieves a TidyPy configuration from the specified location.

        :param location:
            a URI indicating where to retrieve the TidyPy configuration from
        :type location: str
        :param project_path: the full path to the project's base
        :type project_path: str
        :rtype: dict
        """

        raise NotImplementedError()

    @classmethod
    def parse(cls, content, is_pyproject=False):
        """
        A convenience method for parsing a TOML-serialized configuration.

        :param content: a TOML string containing a TidyPy configuration
        :type content: str
        :param is_pyproject:
            whether or not the content is (or resembles) a ``pyproject.toml``
            file, where the TidyPy configuration is located within a key named
            ``tool``.
        :type is_pyproject: bool
        :rtype: dict
        """

        parsed = toml.loads(content)

        if is_pyproject:
            parsed = parsed.get('tool', {})
        parsed = parsed.get('tidypy', {})

        return parsed


class ExtenderError(Exception):
    """
    The base class for all exceptions raised by an Extender during its
    operation.
    """


class DoesNotExistError(ExtenderError):
    """
    An exception indicating that the specified Extender does not exist in the
    current environment.
    """

