"""
CLI Entrypoint
"""
import click
from fest import __version__


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-v', '--version')
def fest():
    """ Export Facebook Page Events to other services.

        See https://github.com/amancevice/fest for details & instructions.
    """
    pass  # pragma: no cover
