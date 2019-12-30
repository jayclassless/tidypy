
from pathlib import Path

from .util import read_file, compile_masks, matches_masks


ALWAYS_EXCLUDED_DIRS = compile_masks([
    r'^\.hg$',
    r'^\.git$',
    r'^\.svn$',
    r'^CVS$',
    r'^\.bzr$',
    r'^__pycache__$',
    r'^\.tox$',
    r'^.+\.egg-info$',
])


class Finder(object):
    """
    A class that encapsulates the logic of finding files in a project that will
    be analyzed.
    """

    def __init__(self, base_path, config):
        """
        :param base_path: the path to the base of the project
        :type base_path: str
        :param config: the configuration to use when searching the project
        :type config: dict
        """

        self.base_path = Path(base_path).resolve()
        self.excludes = compile_masks(config['exclude'])

        self._found = dict()
        self._find(self.base_path)
        self._found = dict([
            (dirname, files)
            for dirname, files in self._found.items()
            if files
        ])

    @property
    def project_path(self):
        """
        The path to the project that this Finder is operating from.
        """

        return str(self.base_path)

    def relative_to_project(self, filepath):
        """
        Reformats a file path to be relative to this Finder's project path.

        :param filepath: the path to reformat
        :type filepath: str or pathlib.Path
        :rtype: str
        """

        return str(Path(filepath).relative_to(self.base_path))

    def _find(self, path):
        for subpath in path.iterdir():
            if subpath.is_dir():
                if not self.is_excluded_dir(subpath):
                    self._found[str(subpath)] = []
                    self._find(subpath)

            elif subpath.is_file():
                if not self.is_excluded(subpath):
                    if str(path) not in self._found:
                        self._found[str(path)] = []
                    self._found[str(path)].append(str(subpath))

    def is_excluded(self, path):
        """
        Determines whether or not the specified file is excluded by the
        project's configuration.

        :param path: the path to check
        :type path: pathlib.Path
        :rtype: bool
        """

        relpath = path.relative_to(self.base_path).as_posix()
        return matches_masks(relpath, self.excludes)

    def is_excluded_dir(self, path):
        """
        Determines whether or not the specified directory is excluded by the
        project's configuration.

        :param path: the path to check
        :type path: pathlib.Path
        :rtype: bool
        """

        if self.is_excluded(path):
            return True
        return matches_masks(path.name, ALWAYS_EXCLUDED_DIRS)

    def files(self, filters=None):
        """
        A generator that produces a sequence of paths to files in the project
        that matches the specified filters.

        :param filters:
            the regular expressions to use when finding files in the project.
            If not specified, all files are returned.
        :type filters: list(str)
        """

        filters = compile_masks(filters or [r'.*'])

        for files in self._found.values():
            for file_ in files:
                relpath = str(Path(file_).relative_to(self.base_path))
                if matches_masks(relpath, filters):
                    yield file_

    def _contains(self, files, masks):
        for file_ in files:
            if matches_masks(file_, masks):
                return True
        return False

    def directories(self, filters=None, containing=None):
        """
        A generator that produces a sequence of paths to directories in the
        project that matches the specified filters.

        :param filters:
            the regular expressions to use when finding directories in the
            project. If not specified, all directories are returned.
        :type filters: list(str)
        :param containing:
            if a directory passes through the specified filters, it is checked
            for the presence of a file that matches one of the regular
            expressions in this parameter.
        :type containing: list(str)
        """

        filters = compile_masks(filters or [r'.*'])
        contains = compile_masks(containing)

        for dirname, files in self._found.items():
            relpath = str(Path(dirname).relative_to(self.base_path))
            if matches_masks(relpath, filters):
                if not contains or self._contains(files, contains):
                    yield dirname

    def packages(self, filters=None):
        """
        A generator that produces a sequence of paths to directories that look
        to be Python packages (e.g., they contain an ``__init__.py``).

        :param filters:
            the regular expressions to use when finding directories in the
            project. If not specified, all directories are returned.
        :type filters: list(str)
        """

        return self.directories(
            filters=filters,
            containing=[r'__init__.py$'],
        )

    def modules(self, filters=None):
        """
        A generator that produces a sequence of paths to files that look to be
        Python modules (e.g., ``*.py``).

        :param filters:
            the regular expressions to use when finding files in the project.
            If not specified, all files are returned.
        :type filters: list(str)
        """

        masks = compile_masks(r'\.py$')
        for file_ in self.files(filters=filters):
            if matches_masks(file_, masks):
                yield file_

    def sys_paths(self, filters=None):
        """
        Produces a list of paths that would be suitable to use in ``sys.path``
        in order to access the Python modules/packages found in this project.

        :param filters:
            the regular expressions to use when finding files in the project.
            If not specified, all files are returned.
        :type filters: list(str)
        """

        paths = set()

        packages = list(self.packages(filters=filters))

        for module in self.modules(filters=filters):
            parent = str(Path(module).parent)
            if parent not in packages:
                paths.add(parent)

        paths.update(self.topmost_directories([
            str(Path(package).parent)
            for package in packages
        ]))

        return list(paths)

    def topmost_directories(self, directories):
        if not directories:
            return []
        directories = sorted(directories)

        topmost = directories[:1]

        for directory in directories[1:]:
            parents = sorted([
                str(parent)
                for parent in Path(directory).parents
            ])
            for parent in parents:
                if parent in topmost:
                    break
            else:
                topmost.append(directory)

        return topmost

    def read_file(self, filepath):
        """
        Retrieves the contents of the specified file.

        This function performs simple caching so that the same file isn't read
        more than once per process.

        :param filepath: the file to read.
        :type filepath: str
        :rtype: str
        """

        return read_file(filepath)

