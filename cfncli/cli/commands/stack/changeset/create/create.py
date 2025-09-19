# -*- encoding: utf-8 -*-
import click
import json
import os

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.runner.commands.stack_changeset_command import StackChangesetOptions, StackChangesetCommand
from cfncli.cli.utils.colormaps import RED


@click.command()
@click.option(
    "--use-previous-template",
    is_flag=True,
    default=False,
    help="Reuse the existing template that is associated with the stack that you are updating.",
)
@click.option(
    "--ignore-no-update",
    "-i",
    is_flag=True,
    default=False,
    help="Ignore error when there are no updates to be performed.",
)
@click.option("--disable-nested", is_flag=True, default=False, help="Disable creation of nested changesets")
@click.option("--show-physical-ids", is_flag=True, default=False, help="Shows physical ID of changeset produced")
@click.option("--store", is_flag=True, default=False, help="Store changeset ARNS for execution in subsequent command")
@click.option(
    "--output", default=".cfn-cli-changesets", help="file path of changeset file store (Default .cfn-cli-changesets)"
)
@click.pass_context
@command_exception_handler
def create(ctx, use_previous_template, ignore_no_update, disable_nested, show_physical_ids, store, output):
    """Create a ChangeSet

    `Combines "aws cloudformation package" and "aws cloudformation create-change-set" command
    into one.  `If stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.
    """
    assert isinstance(ctx.obj, Context)

    if store:
        if os.path.exists(output) and os.path.isfile(output):
            os.remove(output)
        elif os.path.exists(output) and not os.path.isfile(output):
            click.secho(f"ChangeSet output file {output}  exists and is not a file.", fg=RED)
            return

    options = StackChangesetOptions(
        use_previous_template=use_previous_template,
        disable_nested=disable_nested,
        ignore_no_update=ignore_no_update,
        show_physical_ids=show_physical_ids,
    )

    command = StackChangesetCommand(pretty_printer=ctx.obj.ppt, options=options)
    results = ctx.obj.runner.run(command)
    if store:
        changesets = {}
        for stack, result in results.items():
            success, changeset = result
            if success:
                changesets[stack] = changeset.get("ChangeSetId", "")
        if changesets.keys():
            with open(output, "w") as file:
                json.dump(changesets, file)
