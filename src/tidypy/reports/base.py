
from pathlib import Path

import click


class Report(object):
    """
    The base class for TidyPy issue reporters.
    """

    def __init__(self, config, base_path, output_file=None):
        """
        :param config:
            the configuration used during the analysis of the project
        :type config: dict
        :param base_path: the path to the project base directory
        :type base_path: str
        """

        self.config = config
        self.base_path = base_path
        self._output_needs_closing = False
        if output_file:
            self.output_file = output_file
        elif self.config.get('file'):
            self.output_file = click.open_file(
                self.config['file'],
                mode='w',
                encoding='utf-8',
            )
            self._output_needs_closing = True
        else:
            self.output_file = click.get_text_stream('stdout')

    def execute(self, collector):
        """
        Produces the contents of the report.

        Must be implemented by concrete classes.

        :param collector: the collection of issues to report on
        :type collector: tidypy.Collector
        """

    def produce(self, collector):
        self.execute(collector)
        if self._output_needs_closing:
            self.output_file.close()

    def relative_filename(self, filename):
        """
        Generates a path for the specified filename that is relative to the
        project path.

        :param filename: the filename to generate the path for
        :type filename: str
        :rtype: str
        """

        return Path(filename).relative_to(self.base_path).as_posix()

    def output(self, msg, newline=True):
        """
        Writes the specified string to the output target of the report.

        :param msg: the message to output.
        :type msg: str
        :param newline:
            whether or not to append a newline to the end of the message
        :type newline: str
        """

        click.echo(str(msg), nl=newline, file=self.output_file)

