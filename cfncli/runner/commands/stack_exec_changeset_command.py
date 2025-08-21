import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from cfncli.cli.utils.deco import CfnCliException
from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from cfncli.cli.utils.pprint import echo_pair
from .command import Command
from .utils import update_termination_protection, is_changeset_does_not_exist_exception
from cfncli.cli.utils.colormaps import RED, AMBER, GREEN
from .stack_changeset_command import StackChangesetCommand


class StackExecuteChangesetOptions(
    namedtuple(
        "StackExecuteChangeSetOptions",
        ["disable_rollback", "disable_tail_events", "changesets", "ignore_no_exists"],
    )
):
    pass


class StackExecuteChangesetCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # create cfn client
        client = session.client("cloudformation")

        ## ensure we have changeset
        if not self.options.changesets.get(stack_context.stack_key, None):
            if self.options.ignore_no_exists:
                self.ppt.secho(f"ChangeSet for {stack_context.stack_key} does not exist, skipping....", fg=RED)
                return False, None
            raise CfnCliException(f"ChangeSet for {stack_context.stack_key} does not exist")
        changeset_arn = self.options.changesets[stack_context.stack_key]

        # print stack qualified name
        self.ppt.pprint_changeset_with_stack("Executing Changeset", stack_context.stack_key, changeset_arn)

        ## ensure stack status
        try:
            result = self.describe_change_set(client, changeset_arn, parameters)
        except botocore.exceptions.ClientError as ex:
            if is_changeset_does_not_exist_exception(ex):
                if self.options.ignore_no_exists:
                    self.ppt.secho(f"ChangeSet {changeset_arn} does not exist.", fg=RED)
                    return False, None
                else:
                    raise CfnCliException(f"ChangeSet {changeset_arn} does not exist")
            else:
                raise

        changeset_type, is_new_stack = StackChangesetCommand.check_changeset_type(client, parameters)

        # check if changeset is executable
        if result["Status"] not in ("AVAILABLE", "CREATE_COMPLETE"):
            raise CfnCliException(
                f"ChangeSet {changeset_arn} not available. Status is {result.get('Status', 'unknown')}"
            )

        # check execution status
        if result["ExecutionStatus"] not in ("AVAILABLE"):
            raise CfnCliException(
                f"ChangeSet {changeset_arn} not executable. Status is {result.get('ExecutionStatus', 'unknown')}"
            )

        # print stack qualified name
        self.ppt.pprint_session(session)

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

        client_request_token = "awscfncli-sync-{}".format(uuid.uuid1())
        client.execute_change_set(
            ChangeSetName=changeset_arn,
            ClientRequestToken=client_request_token,
            DisableRollback=parameters.get("DisableRollback", False),
        )

        cfn = session.resource("cloudformation")
        stack = cfn.Stack(parameters["StackName"])

        if changeset_type == "CREATE":
            self.ppt.wait_until_deploy_complete(session, stack, self.options.disable_tail_events)
        else:
            self.ppt.wait_until_update_complete(session, stack, self.options.disable_tail_events)
        self.ppt.secho("ChangeSet execution complete.", fg=GREEN)

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def describe_change_set(self, client, changeset_arn, parameters):
        return client.describe_change_set(
            ChangeSetName=changeset_arn,
            IncludePropertyValues=True,
        )
