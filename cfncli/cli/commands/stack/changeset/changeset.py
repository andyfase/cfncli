# -*- encoding: utf-8 -*-
import click

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.runner.commands.stack_changeset_command import StackChangesetOptions, \
    StackChangesetCommand


@click.command()
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--disable-tail-events', is_flag=True, default=False,
              help='Disable tailing of cloudformation events')
@click.option('--disable-nested', is_flag=True, default=False,
              help='Disable creation of nested changesets')
@click.pass_context
@command_exception_handler
def changeset(ctx, use_previous_template, disable_tail_events, disable_nested):
    """Create a ChangeSet

    `Combines "aws cloudformation package" and "aws cloudformation create-change-set" command
    into one.  `If stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.
    """
    assert isinstance(ctx.obj, Context)

    options = StackChangesetOptions(
        use_previous_template=use_previous_template,
        disable_tail_events=disable_tail_events,
        disable_nested=disable_nested
    )

    command = StackChangesetCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
