
import traceback


class Tool(object):
    """
    The base class for TidyPy tools.
    """

    @classmethod
    def can_be_used(cls):
        """
        Indicates whether or not this tool can be executed now. Useful when you
        need to check for certain environmental conditions (e.g., Python
        version, dependency availability, etc).

        Unless overridden, always returns ``True``.

        :rtype: bool
        """

        return True

    @classmethod
    def get_default_config(cls):
        """
        Produces a tool configuration stanza that acts as the base/default for
        this tool.

        rtype: dict
        """

        return {
            'use': True,
            'filters': [],
            'disabled': [],
            'options': {},
        }

    @classmethod
    def get_all_codes(cls):
        """
        Produces a sequence of all the issue codes this tool is capable of
        generating. Elements in this sequence must all be 2-element tuples,
        where the first element is the code, and the second is a textual
        description of what the code means.

        Must be implemented by concrete classes.

        :returns: tuple of tuples containing two strings each
        """

        raise NotImplementedError()

    def __init__(self, config):
        """
        :param config: the tool configuration to use during execution
        :type config: dict
        """

        #: The tool's configuration to use during its execution.
        self.config = config

    def execute(self, finder):
        """
        Analyzes the project and generates a list of issues found during that
        analysis.

        Must be implemented by concrete classes.

        :param finder:
            the Finder class that should be used to identify the files or
            directories that the tool will analyze.
        :type finder: tidypy.Finder
        :rtype: list(tidypy.Issue)
        """

        raise NotImplementedError()


class PythonTool(Tool):
    """
    A convenience abstract class that automatically sets the ``filters`` in the
    tool configuration to target Python source files.
    """

    # pylint: disable=abstract-method

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.py$',
        ]
        return config


class Issue(object):
    """
    A class that encapsulates an issue found during the analysis of a project.
    """

    #: A string containing name of the tool that found the issue.
    tool = None

    #: A string containing a code that identifies the type of issue found.
    code = None

    #: A string containing a description of the issue.
    message = None

    #: A string containing the full path to the file where the issue was found.
    filename = None

    #: The line number within the file where the issue was found (if known).
    #: The first line in a file is notated as 1 (not zero).
    line = None

    #: The character number within the line of the file where the issue was
    #: found (if known). The first column in a line is notated as 1 (not zero).
    character = None

    #: A character indicating the comparable pylint category this issue would
    #: fall into: E=error, W=warning, R=refactor, C=convention
    pylint_type = 'E'

    def __init__(
            self,
            code=None,
            message=None,
            filename=None,
            line=None,
            character=None):
        self.code = code
        self.message = message
        self.filename = filename
        self.line = line if line is not None else 1
        self.character = character or None

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join([
                repr(self.code),
                repr(self.message),
                repr(self.filename),
                repr(self.line),
                repr(self.character),
            ]),
        )


class TidyPyIssue(Issue):
    """
    The base class for all TidyPy application issues that are produced.
    """

    tool = 'tidypy'
    pylint_type = 'F'


class UnknownIssue(TidyPyIssue):
    """
    A completely unanticipated exception/problem was encountered during the
    execution of a tool.
    """

    def __init__(self, exc, filename):
        super().__init__(
            'unexpected',
            'Unexpected error (%s)' % (exc,),
            filename,
        )


class AccessIssue(TidyPyIssue):
    """
    An issue indicating that a file/directory cannot be accessed (typically
    due to permissions).
    """

    def __init__(self, exc, filename):
        super().__init__(
            'access',
            'Cannot access file (%s)' % (exc,),
            filename,
        )


class ParseIssue(TidyPyIssue):
    """
    An issue indicating that a file could not be parsed as expected (e.g., a
    Python source file with invalid syntax).
    """

    def __init__(self, exc, filename, line=None, character=None):
        if isinstance(exc, SyntaxError):
            line = exc.lineno
            character = exc.offset

        super().__init__(
            'parse',
            'Unable to parse file (%s)' % (exc,),
            filename,
            line,
            character,
        )


class ToolIssue(TidyPyIssue):
    """
    An issue indicating that a tool completely crashed/failed during its
    execution.
    """

    def __init__(self, message, project_path, details=None, failure=False):
        if details:
            if isinstance(details, tuple):
                details = ''.join(traceback.format_exception(*details))
            message = '%s:\n%s' % (message, details)

        super().__init__(
            'tool',
            message,
            project_path,
        )

        self.pylint_type = 'F' if failure else 'E'

