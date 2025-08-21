import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from cfncli.cli.utils.deco import CfnCliException
from cfncli.cli.utils.pprint import echo_pair
from .command import Command
from .utils import update_termination_protection
from cfncli.cli.utils.colormaps import CHANGESET_STATUS_TO_COLOR, RED, AMBER, GREEN


class StackChangesetOptions(
    namedtuple(
        "StackChangesetOptions", ["use_previous_template", "disable_tail_events", "ignore_no_update", "disable_nested"]
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
        changeset_type, is_new_stack = StackChangesetCommand.check_changeset_type(client, parameters)

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
            result = self.create_change_set(client, parameters)
            changeset_id = result["Id"]
            echo_pair("ChangeSet ARN", changeset_id)

            self.ppt.wait_until_changset_complete(client, changeset_id)
            result = self.describe_change_set(client, parameters["ChangeSetName"], parameters)

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

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def create_change_set(self, client, parameters):
        return client.create_change_set(**parameters)

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def describe_change_set(self, client, changeset_name, parameters):
        return client.describe_change_set(
            ChangeSetName=changeset_name,
            StackName=parameters["StackName"],
            IncludePropertyValues=True,
        )

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    @staticmethod
    def check_changeset_type(client, parameters):
        try:
            # check whether stack is already created.
            status = client.describe_stacks(StackName=parameters["StackName"])
            stack_status = status["Stacks"][0]["StackStatus"]
        except botocore.exceptions.ClientError as e:

            if is_rate_limited_exception(e):
                # stack might exist but we got Throttling error, retry is needed so rerasing exception
                raise
            # stack not yet created
            is_new_stack = True
            changeset_type = "CREATE"
        else:
            if stack_status == "REVIEW_IN_PROGRESS":
                # first ChangeSet execution failed, create "new stack" changeset again
                is_new_stack = True
                changeset_type = "CREATE"
            else:
                # updating an existing stack
                is_new_stack = False
                changeset_type = "UPDATE"
        return changeset_type, is_new_stack
