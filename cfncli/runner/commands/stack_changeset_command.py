import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from cfncli.cli.utils.deco import CfnCliException
from cfncli.cli.utils.pprint import echo_pair
from .command import Command
from .utils import (
    update_termination_protection,
    check_changeset_type,
    create_change_set,
    describe_change_set,
    is_changeset_no_changes,
)
from cfncli.cli.utils.colormaps import CHANGESET_STATUS_TO_COLOR, RED, AMBER, GREEN


class StackChangesetOptions(
    namedtuple(
        "StackChangesetOptions", ["use_previous_template", "ignore_no_update", "disable_nested", "show_physical_ids"]
    )
):
    pass


class StackChangesetCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print stack qualified name
        self.ppt.pprint_stack_name(stack_context.stack_key, parameters["StackName"], "Generating Changeset for stack ")
        self.ppt.pprint_session(session)

        if self.options.use_previous_template:
            parameters.pop("TemplateBody", None)
            parameters.pop("TemplateURL", None)
            parameters["UsePreviousTemplate"] = True
        else:
            stack_context.run_packaging()

        # create cfn client
        client = session.client("cloudformation")

        # get changeset type: CREATE or UPDATE
        changeset_type, is_new_stack = check_changeset_type(client, parameters["StackName"])

        # set nested based on input AND only if not new stack
        if is_new_stack:
            self.ppt.secho("Disabling nested changsets for initial creation.", fg=AMBER)
            parameters["IncludeNestedStacks"] = False
        else:
            parameters["IncludeNestedStacks"] = False if self.options.disable_nested else True

        # prepare stack parameters
        parameters["ChangeSetType"] = changeset_type
        parameters.pop("StackPolicyBody", None)
        parameters.pop("StackPolicyURL", None)
        parameters.pop("DisableRollback", None)
        termination_protection = parameters.pop("EnableTerminationProtection", None)

        result = {}
        while True:  ## return in loop on succes / fail if not retry requred
            # generate a unique changeset name
            parameters["ChangeSetName"] = "%s-%s" % (parameters["StackName"], str(uuid.uuid1()))

            # print changeset config
            echo_pair("ChangeSet Name", parameters["ChangeSetName"])
            echo_pair("ChangeSet Type", changeset_type)
            self.ppt.pprint_parameters(parameters)

            # create changeset
            try:
                result = create_change_set(client, parameters)
            except Exception as e:
                if is_changeset_no_changes(e):
                    if self.options.ignore_no_update:
                        self.ppt.secho(
                            f"ChangeSet for {stack_context.stack_key} contains no updates, skipping...", fg=RED
                        )
                        return False, result
                    else:
                        raise CfnCliException(
                            f"Changeset for {stack_context.stack_key} contains no updates, use -i if this is expected"
                        )
                raise e
            changeset_id = result["Id"]
            if self.options.show_physical_ids:
                echo_pair("ChangeSet ARN", changeset_id)

            self.ppt.wait_until_changset_complete(client, changeset_id)
            result = describe_change_set(client, changeset_arn=changeset_id)

            ## check explicity for FAILED with nested stacks
            if result["Status"] == "FAILED" and parameters.get("IncludeNestedStacks", False):
                echo_pair(
                    "ChangeSet creation failed",
                    f"Reason: {result.get('StatusReason', 'unknown')}",
                    key_style=CHANGESET_STATUS_TO_COLOR["FAILED"],
                    value_style=CHANGESET_STATUS_TO_COLOR["FAILED"],
                )
                ## dont retry if the failure is due to no changes
                if "didn't contain changes" in result.get("StatusReason", ""):
                    if self.options.ignore_no_update:
                        self.ppt.secho(
                            f"ChangeSet for {stack_context.stack_key} contains no updates, skipping...", fg=RED
                        )
                        return False, result
                    else:
                        raise CfnCliException(
                            f"Changeset for {stack_context.stack_key} contains no updates, use -i if this is expected"
                        )
                self.ppt.secho("Will RETRY WITHOUT nested changeset support", fg=RED)
                parameters["IncludeNestedStacks"] = False
                continue

            ## check for any other not good status
            if result["Status"] not in ("AVAILABLE", "CREATE_COMPLETE"):
                raise CfnCliException(f"ChangeSet creation failed. {result['StatusReason']}")

            # fetch nested changesets if needed then pretty print
            if parameters["IncludeNestedStacks"]:
                self.ppt.fetch_nested_changesets(client, result)
            self.ppt.pprint_changeset(result)
            self.ppt.secho("ChangeSet creation complete.", fg=GREEN)
            return (True, result)
