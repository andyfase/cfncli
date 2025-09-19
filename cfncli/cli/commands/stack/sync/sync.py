# -*- encoding: utf-8 -*-
import click

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.runner.commands.stack_sync_command import StackSyncOptions, StackSyncCommand


@click.command()
@click.option("--no-wait", "-w", is_flag=True, default=False, help="Exit immediately after ChangeSet is created.")
@click.option("--confirm", is_flag=True, default=False, help="Review changes before execute the ChangeSet")
@click.option(
    "--ignore-no-update",
    "-i",
    is_flag=True,
    default=False,
    help="Ignore error when there are no updates to be performed.",
)
@click.option(
    "--use-previous-template",
    is_flag=True,
    default=False,
    help="Reuse the existing template that is associated with the " "stack that you are updating.",
)
@click.option(
    "--disable-rollback",
    is_flag=True,
    default=False,
    help="Disable rollback if stack update fails. You can specify "
    "either DisableRollback or OnFailure, but not both. "
    'Setting this option overwrites "DisableRollback" '
    "in the stack configuration file.",
)
@click.option("--disable-tail-events", is_flag=True, default=False, help="Disable tailing of cloudformation events")
@click.option("--show-physical-ids", is_flag=True, default=False, help="Shows physical IDs in tail events")
@click.option("--disable-nested", is_flag=True, default=False, help="Disable creation of nested changesets")
@click.pass_context
@command_exception_handler
def sync(
    ctx,
    no_wait,
    confirm,
    ignore_no_update,
    use_previous_template,
    disable_rollback,
    disable_tail_events,
    show_physical_ids,
    disable_nested,
):
    """Create and execute ChangeSets (SAM)

    Combines "aws cloudformation package" and "aws cloudformation deploy" command
    into one.  If stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.
    """
    assert isinstance(ctx.obj, Context)

    options = StackSyncOptions(
        no_wait=no_wait,
        confirm=confirm,
        use_previous_template=use_previous_template,
        disable_rollback=disable_rollback,
        disable_tail_events=disable_tail_events,
        disable_nested=disable_nested,
        show_physical_ids=show_physical_ids,
        ignore_no_update=ignore_no_update,
    )

    command = StackSyncCommand(pretty_printer=ctx.obj.ppt, options=options)

    ctx.obj.runner.run(command)
