import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from cfncli.cli.utils.pprint import echo_pair
from .command import Command
from .utils import update_termination_protection
from cfncli.cli.utils.colormaps import RED, AMBER, GREEN


class StackChangesetOptions(
    namedtuple("StackChangesetOptions", ["use_previous_template", "disable_tail_events", "disable_nested"])
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

        # generate a unique changeset name
        changeset_name = "%s-%s" % (parameters["StackName"], str(uuid.uuid1()))

        # get changeset type: CREATE or UPDATE
        changeset_type, is_new_stack = self.check_changeset_type(client, parameters)

        # set nested based on input AND only if not new stack
        if is_new_stack:
            self.ppt.secho("Disabling nested changsets for initial creation.", fg=AMBER)
            parameters["IncludeNestedStacks"] = False
        else:
            parameters["IncludeNestedStacks"] = False if self.options.disable_nested else True

        # prepare stack parameters
        parameters["ChangeSetName"] = changeset_name
        parameters["ChangeSetType"] = changeset_type
        parameters.pop("StackPolicyBody", None)
        parameters.pop("StackPolicyURL", None)
        parameters.pop("DisableRollback", None)
        termination_protection = parameters.pop("EnableTerminationProtection", None)

        self.ppt.pprint_parameters(parameters)

        # create changeset
        echo_pair("ChangeSet Name", changeset_name)
        echo_pair("ChangeSet Type", changeset_type)

        result = self.create_change_set(client, parameters)
        changeset_id = result["Id"]
        echo_pair("ChangeSet ARN", changeset_id)

        self.ppt.wait_until_changset_complete(client, changeset_id)

        result = self.describe_change_set(client, changeset_name, parameters)
        if parameters["IncludeNestedStacks"]:
            self.ppt.fetch_nested_changesets(client, result)
        self.ppt.pprint_changeset(result)

        # check whether changeset is executable
        if result["Status"] not in ("AVAILABLE", "CREATE_COMPLETE"):
            self.ppt.secho("ChangeSet creation failed.", fg=RED)
            return
        self.ppt.secho("ChangeSet creation complete.", fg=GREEN)

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
    def check_changeset_type(self, client, parameters):
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
