import click

from six import text_type

from ..util import Path


class Report(object):
    def __init__(self, config, base_path, output_file=None):
        self.config = config
        self.base_path = base_path
        self._output_needs_closing = False
        if output_file:
            self.output_file = output_file
        elif 'file' in self.config:
            self.output_file = click.open_file(
                self.config['file'],
                mode='w',
                encoding='utf-8',
            )
            self._output_needs_closing = True
        else:
            self.output_file = click.get_text_stream('stdout')

    def execute(self, collector):
        pass

    def produce(self, collector):
        self.execute(collector)
        if self._output_needs_closing:
            self.output_file.close()

    def relative_filename(self, filename):
        return Path(filename).relative_to(self.base_path).as_posix()

    def output(self, msg, newline=True):
        click.echo(text_type(msg), nl=newline, file=self.output_file)

