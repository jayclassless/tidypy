import os.path

import click

from six import text_type


class Report(object):
    def __init__(self, config, base_path, output_file=None):
        self.config = config
        self.base_path = base_path
        if output_file:
            self.output_file = output_file
        elif 'file' in self.config:
            self.output_file = click.open_file(
                self.config['file'],
                mode='w',
                encoding='utf-8',
            )
        else:
            self.output_file = click.get_text_stream('stdout')

    def execute(self, collector):
        pass

    def relative_filename(self, filename):
        return os.path.relpath(filename, self.base_path)

    def output(self, msg, newline=True):
        click.echo(text_type(msg), nl=newline, file=self.output_file)
