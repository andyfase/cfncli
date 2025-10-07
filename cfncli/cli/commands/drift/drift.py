import click

from .detect.detect import detect
from .diff.diff import diff


@click.group(name="drift")
@click.pass_context
def cli(ctx):
    """Drift detection sub-commands."""
    pass


cli.add_command(detect)
cli.add_command(diff)
