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


class StackSyncOptions(
    namedtuple(
        "StackSyncOptions",
        ["no_wait", "confirm", "use_previous_template", "disable_rollback", "disable_tail_events", "disable_nested"],
    )
):
    pass


class StackSyncCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print stack qualified name
        self.ppt.pprint_stack_name(stack_context.stack_key, parameters["StackName"], "Syncing stack ")
        self.ppt.pprint_session(session)

        ## Create ChangeSet uring ChangeSet class - this performs all packaging etc, hence this class does not need too.
        command = StackChangesetCommand(self.ppt, self.options)
        changeset_name, result = command.run(stack_context)

        # check whether changeset is executable
        if result["Status"] not in ("AVAILABLE", "CREATE_COMPLETE"):
            self.ppt.secho("ChangeSet not executable.", fg=RED)
            return

        # create cfn client
        client = session.client("cloudformation")

        # overwrite options based on CLI params
        if self.options.disable_rollback:
            parameters["DisableRollback"] = self.options.disable_rollback

        # prepare stack parameters
        parameters.pop("StackPolicyBody", None)
        parameters.pop("StackPolicyURL", None)
        termination_protection = parameters.pop("EnableTerminationProtection", None)

        self.ppt.pprint_parameters(parameters)
        # termination protection should be set after the creation of stack
        # or changeset
        update_termination_protection(session, termination_protection, parameters["StackName"], self.ppt)

        if self.options.confirm:
            if self.options.no_wait:
                return
            if not self.ppt.confirm("Do you want to execute ChangeSet?"):
                return

        client_request_token = "awscfncli-sync-{}".format(uuid.uuid1())
        self.ppt.secho("Executing ChangeSet...")
        client.execute_change_set(
            ChangeSetName=changeset_name,
            StackName=parameters["StackName"],
            ClientRequestToken=client_request_token,
            DisableRollback=parameters.get("DisableRollback", False),
        )

        cfn = session.resource("cloudformation")
        stack = cfn.Stack(parameters["StackName"])
        if self.options.no_wait:
            self.ppt.secho("ChangeSet execution started.")
        else:
            if parameters["ChangeSetType"] == "CREATE":
                self.ppt.wait_until_deploy_complete(session, stack, self.options.disable_tail_events)
            else:
                self.ppt.wait_until_update_complete(session, stack, self.options.disable_tail_events)
            self.ppt.secho("ChangeSet execution complete.", fg=GREEN)