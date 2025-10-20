import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from cfncli.cli.utils.pprint import echo_pair
from .command import Command
from .utils import update_termination_protection
from cfncli.cli.utils.colormaps import RED, AMBER, GREEN
from .stack_changeset_command import StackChangesetCommand
from .stack_exec_changeset_command import StackExecuteChangesetCommand, StackExecuteChangesetOptions


class StackSyncOptions(
    namedtuple(
        "StackSyncOptions",
        [
            "no_wait",
            "confirm",
            "use_previous_template",
            "disable_rollback",
            "disable_tail_events",
            "disable_nested",
            "show_physical_ids",
            "ignore_no_update",
        ],
    )
):
    pass


class StackSyncCommand(Command):
    def run(self, stack_context):
        # stack contexts
        parameters = stack_context.parameters

        # print stack qualified name
        self.ppt.pprint_stack_name(stack_context.stack_key, parameters["StackName"], "Syncing stack ")

        ## Create ChangeSet using ChangeSet class - this performs all packaging etc
        command = StackChangesetCommand(self.ppt, self.options)
        success, changeset = command.run(stack_context)

        if not success or not changeset.get("ChangeSetId", None):
            self.ppt.secho(f"ChangeSet creation failed - cannot continue sync", fg=RED)
            return

        if self.options.confirm:
            if self.options.no_wait:
                return
            if not self.ppt.confirm("Do you want to execute ChangeSet?"):
                return

        ## Execute ChangeSet using ExecuteChangeSet class
        command = StackExecuteChangesetCommand(
            self.ppt,
            StackExecuteChangesetOptions(
                changesets={stack_context.stack_key: changeset["ChangeSetId"]},
                disable_tail_events=self.options.disable_tail_events,
                disable_rollback=self.options.disable_rollback,
                show_physical_ids=self.options.show_physical_ids,
                ignore_no_exists=False,  ### should never get here as we just created the changeset
            ),
        )
        command.run(stack_context)
        self.ppt.secho("Stack sync complete.", fg="green")
