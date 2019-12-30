
import configparser
import os.path

from ..config import get_project_config
from ..core import execute_tools
from ..reports.console import ConsoleReport


def hook(ui, repo, **kwargs):  # pylint: disable=unused-argument,invalid-name
    cfg = get_project_config(repo.root)
    collector = execute_tools(cfg, repo.root)

    report = ConsoleReport(cfg, repo.root)
    report.execute(collector)

    strict = ui.configbool('tidypy', 'strict', default=False)

    if strict and collector.issue_count() > 0:
        return 1

    return 0


class MercurialHook(object):
    def get_hgrc(self, path, ensure_exists=False):
        if not os.path.isdir(path):
            return None

        hg_dir = os.path.join(path, '.hg')
        if not os.path.exists(hg_dir):
            return None

        hgrc = os.path.join(hg_dir, 'hgrc')
        if not os.path.exists(hgrc):
            if ensure_exists:
                open(hgrc, 'w').close()
                return hgrc
            return None
        return hgrc

    def install(self, path, strict):
        hgrc = self.get_hgrc(path, ensure_exists=True)
        if not hgrc:
            raise Exception(
                'Could not find/create Mercurial configuration in: %s' % (
                    path,
                )
            )

        config = configparser.ConfigParser()
        config.read(hgrc)

        if not config.has_section('hooks'):
            config.add_section('hooks')
        config.set(
            'hooks',
            'precommit.tidypy',
            'python:tidypy.plugin.mercurial.hook',
        )

        if not config.has_section('tidypy'):
            config.add_section('tidypy')
        config.set('tidypy', 'strict', str(strict))

        with open(hgrc, 'w') as config_file:
            config.write(config_file)

    def remove(self, path):
        hgrc = self.get_hgrc(path)
        if not hgrc:
            raise Exception(
                'Could not find Mercurial configuration in: %s' % (
                    path,
                )
            )

        config = configparser.ConfigParser()
        config.read(hgrc)

        if config.has_section('hooks'):
            config.remove_option('hooks', 'precommit.tidypy')

        if config.has_section('tidypy'):
            config.remove_section('tidypy')

        with open(hgrc, 'w') as config_file:
            config.write(config_file)

