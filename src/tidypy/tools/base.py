
import traceback


class Tool(object):
    @classmethod
    def can_be_used(cls):
        return True

    @classmethod
    def get_default_config(cls):
        return {
            'use': True,
            'filters': [],
            'disabled': [],
            'options': {},
        }

    @classmethod
    def get_all_codes(cls):
        raise NotImplementedError()

    def __init__(self, config):
        self.config = config

    def execute(self, finder):
        raise NotImplementedError()


class PythonTool(Tool):
    # pylint: disable=abstract-method

    @classmethod
    def get_default_config(cls):
        config = Tool.get_default_config()
        config['filters'] = [
            r'\.py$',
        ]
        return config


class Issue(object):
    tool = None
    code = None
    message = None
    filename = None
    line = None
    character = None
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
    tool = 'tidypy'
    pylint_type = 'F'


class UnknownIssue(TidyPyIssue):
    def __init__(self, exc, filename):
        super(UnknownIssue, self).__init__(
            'unexpected',
            'Unexpected error (%s)' % (exc,),
            filename,
        )


class AccessIssue(TidyPyIssue):
    def __init__(self, exc, filename):
        super(AccessIssue, self).__init__(
            'access',
            'Cannot access file (%s)' % (exc,),
            filename,
        )


class ParseIssue(TidyPyIssue):
    def __init__(self, exc, filename, line=None, character=None):
        if isinstance(exc, SyntaxError):
            line = exc.lineno
            character = exc.offset

        super(ParseIssue, self).__init__(
            'parse',
            'Unable to parse file (%s)' % (exc,),
            filename,
            line,
            character,
        )


class ToolIssue(TidyPyIssue):
    def __init__(self, message, project_path, details=None, failure=False):
        if details:
            if isinstance(details, tuple):
                details = ''.join(traceback.format_exception(*details))
            message = '%s:\n%s' % (message, details)

        super(ToolIssue, self).__init__(
            'tool',
            message,
            project_path,
        )

        self.pylint_type = 'F' if failure else 'E'

