import click

from .create.create import create
from .exec.exec import exec


@click.group(name="changeset")
@click.pass_context
def changeset(ctx):
    """Changeset operation sub-commands."""
    pass


changeset.add_command(create)
changeset.add_command(exec)
