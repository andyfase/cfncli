# -*- encoding: utf-8 -*-
import click
import json
import os
from cfncli.cli.utils.colormaps import RED
from cfncli.cli.utils.deco import CfnCliException

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.runner.commands.stack_exec_changeset_command import (
    StackExecuteChangesetOptions,
    StackExecuteChangesetCommand,
)


@click.command()
@click.option("--disable-tail-events", is_flag=True, default=False, help="Disable tailing of cloudformation events")
@click.option("--show-physical-ids", is_flag=True, default=False, help="Shows physical IDs in tail events")
@click.option(
    "--ignore-no-exists",
    "-i",
    is_flag=True,
    default=False,
    help="Ignore error when there are no changeset for selected stack.",
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
@click.option(
    "--input", default=".cfn-cli-changesets", help="file path of changeset file store (Default .cfn-cli-changesets)"
)
@click.pass_context
@command_exception_handler
def exec(ctx, disable_tail_events, show_physical_ids, disable_rollback, input, ignore_no_exists):
    """Execute a existing ChangeSet

    `Combines "aws cloudformation package" and "aws cloudformation create-change-set" command
    into one.  `If stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.
    """
    assert isinstance(ctx.obj, Context)

    ## check changeset file exists otherwise error and exit
    if not os.path.exists(input) or not os.path.isfile(input):
        raise CfnCliException(
            f"ChangeSet file {input} does not exist - ensure to create changesets with '--store' parameter before running this command.",
        )

    with open(input) as f:
        changesets = json.load(f)
        options = StackExecuteChangesetOptions(
            show_physical_ids=show_physical_ids,
            disable_tail_events=disable_tail_events,
            disable_rollback=disable_rollback,
            changesets=changesets,
            ignore_no_exists=ignore_no_exists,
        )

        command = StackExecuteChangesetCommand(pretty_printer=ctx.obj.ppt, options=options)
        ctx.obj.runner.run(command)
