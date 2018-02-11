import sys

from coverage import CoveragePlugin


class MyConfigPlugin(CoveragePlugin):
    def configure(self, config):
        opt_name = 'report:exclude_lines'
        exclude_lines = config.get_option(opt_name)

        if sys.version_info < (3,):
            exclude_lines.append('pragma: PY3')
        else:
            exclude_lines.append('pragma: PY2')

        config.set_option(opt_name, exclude_lines)


def coverage_init(reg, options):  # noqa: unused-argument
    reg.add_configurer(MyConfigPlugin())

