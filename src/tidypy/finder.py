
from six import iteritems, itervalues, text_type

from .util import read_file, compile_masks, matches_masks, Path


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
    def __init__(self, base_path, config):
        self.base_path = Path(base_path).resolve()
        self.excludes = compile_masks(config['exclude'])

        self._found = dict()
        self._find(self.base_path)
        self._found = dict([
            (dirname, files)
            for dirname, files in iteritems(self._found)
            if files
        ])

    @property
    def project_path(self):
        return text_type(self.base_path)

    def relative_to_project(self, filepath):
        return text_type(Path(filepath).relative_to(self.base_path))

    def _find(self, path):
        for subpath in path.iterdir():
            if subpath.is_dir():
                if not self.is_excluded_dir(subpath):
                    self._found[text_type(subpath)] = []
                    self._find(subpath)

            elif subpath.is_file():
                if not self.is_excluded(subpath):
                    if text_type(path) not in self._found:
                        self._found[text_type(path)] = []
                    self._found[text_type(path)].append(text_type(subpath))

    def is_excluded(self, path):
        relpath = path.relative_to(self.base_path).as_posix()
        return matches_masks(relpath, self.excludes)

    def is_excluded_dir(self, path):
        if self.is_excluded(path):
            return True
        return matches_masks(path.name, ALWAYS_EXCLUDED_DIRS)

    def files(self, filters=None):
        filters = compile_masks(filters or [r'.*'])

        for files in itervalues(self._found):
            for file_ in files:
                relpath = text_type(Path(file_).relative_to(self.base_path))
                if matches_masks(relpath, filters):
                    yield file_

    def _contains(self, files, masks):
        for file_ in files:
            if matches_masks(file_, masks):
                return True
        return False

    def directories(self, filters=None, containing=None):
        filters = compile_masks(filters or [r'.*'])
        contains = compile_masks(containing)

        for dirname, files in iteritems(self._found):
            relpath = text_type(Path(dirname).relative_to(self.base_path))
            if matches_masks(relpath, filters):
                if not contains or self._contains(files, contains):
                    yield dirname

    def packages(self, filters=None):
        return self.directories(
            filters=filters,
            containing=[r'__init__.py$'],
        )

    def modules(self, filters=None):
        masks = compile_masks(r'\.py$')
        for file_ in self.files(filters=filters):
            if matches_masks(file_, masks):
                yield file_

    def sys_paths(self, filters=None):
        paths = set()

        packages = list(self.packages(filters=filters))

        for module in self.modules(filters=filters):
            parent = text_type(Path(module).parent)
            if parent not in packages:
                paths.add(parent)

        paths.update(self.topmost_directories([
            text_type(Path(package).parent)
            for package in packages
        ]))

        return list(paths)

    def topmost_directories(self, directories):
        if not directories or len(directories) < 1:
            return []
        directories = sorted(directories)

        topmost = directories[:1]

        for directory in directories[1:]:
            parents = sorted([
                text_type(parent)
                for parent in Path(directory).parents
            ])
            for parent in parents:
                if parent in topmost:
                    break
            else:
                topmost.append(directory)

        return topmost

    def read_file(self, filepath):
        return read_file(filepath)

