"""Proxy interfaces for cli print."""

import backoff
import botocore.exceptions
import click

from .colormaps import (
    CHANGESET_STATUS_TO_COLOR,
    CHANGESET_ACTION_TO_COLOR,
    CHANGESET_REPLACEMENT_TO_COLOR,
    DRIFT_STATUS_TO_COLOR,
    DRIFT_RESOURCE_TYPE_TO_COLOR,
    STACK_STATUS_TO_COLOR,
    CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR,
)
from .common import is_rate_limited_exception, is_not_rate_limited_exception
from .events import start_tail_stack_events_daemon
from .pager import custom_paginator
from cfncli.runner.commands.utils import describe_change_set, is_stack_does_not_exist_exception


def echo_list(key, list_styles_pairs, indent=0, sep=": "):
    key = " " * indent + key + sep
    click.secho(key, bold=False, nl=False)

    pairs = [
        (list_styles_pairs[i], list_styles_pairs[i + 1])
        for i in range(0, len(list_styles_pairs), 2)
        if i + 1 < len(list_styles_pairs)
    ]

    for i, (value, style) in enumerate(pairs):
        is_last = i == len(pairs) - 1
        if style:
            click.secho(value, nl=is_last, **style)
        else:
            click.secho(value, nl=is_last)


def echo_pair(key, value=None, indent=0, value_style=None, key_style=None, sep=": "):
    """Pretty print a key value pair
    :param key: The key
    :param value: The value
    :param indent: Number of leading spaces
    :param value_style: click.style parameters of value as a dict, default is none
    :param key_style:  click.style parameters of value as a dict, default is bold text
    :param sep: separator between key and value
    """
    assert key
    key = " " * indent + key + sep
    if key_style is None:
        click.secho(key, bold=False, nl=False)
    else:
        click.secho(key, nl=False, **key_style)

    if value is None:
        click.echo("")
    else:

        if value_style is None:
            click.echo(value)
        else:
            click.secho(value, **value_style)


def echo_pair_if_exists(data, key, value, indent=2, key_style=None, value_style=None):
    if value in data:
        echo_pair(
            key,
            data[value],
            indent=indent,
            key_style=key_style,
            value_style=value_style,
        )


class StackPrettyPrinter(object):
    """Pretty print stack parameter, status and events

    Calls click.secho to do the heavy lifting.
    """

    def __init__(self, verbosity=0):
        self.verbosity = verbosity
        self.nested_changesets = {}

    def secho(self, text, nl=True, err=False, color=None, **styles):
        click.secho(text, nl=nl, err=err, color=color, **styles)

    def echo_pair(self, key, value=None, indent=0, value_style=None, key_style=None, sep=": "):
        echo_pair(key, value=value, indent=indent, value_style=value_style, key_style=key_style, sep=sep)

    def confirm(self, *args, **argv):
        return click.confirm(*args, **argv)

    def pprint_stack_name(self, qualified_name, stack_name, prefix=None):
        """Print stack qualified name"""
        if prefix:
            click.secho(prefix, bold=True, nl=False)
        click.secho(qualified_name, bold=True)
        echo_pair("StackName", stack_name)

    def pprint_changeset_with_stack(self, operation, stack_name, changeset_arn):
        click.secho(f"{operation} ", bold=False, nl=False)
        click.secho(changeset_arn, bold=True, nl=False)
        click.secho(" on stack ", bold=False, nl=False)
        click.secho(stack_name, bold=True)

    def pprint_session(self, session, retrieve_identity=True):
        """Print boto3 session"""
        echo_pair("Profile", session.profile_name)
        echo_pair("Region", session.region_name)

        if retrieve_identity:
            sts = session.client("sts")
            identity = sts.get_caller_identity()
            echo_pair("Account", identity["Account"])
            echo_pair("Identity", identity["Arn"])

    def pprint_metadata(self, metadata):
        """Print stack metadata"""
        if self.verbosity > 0:
            click.secho("--- Stack Metadata ---", fg="white", dim=True)
            for k, v in metadata.items():
                echo_pair(k, repr(v), key_style={"fg": "white", "dim": True}, value_style={"fg": "white", "dim": True})

    def pprint_parameters(self, parameters):
        """Print stack parameters"""
        if self.verbosity > 0:
            click.secho("--- Stack Creation Parameters ---", fg="white", dim=True)
            for k, v in parameters.items():
                if k not in ("TemplateBody", "StackPolicyBody"):
                    echo_pair(
                        k, repr(v), key_style={"fg": "white", "dim": True}, value_style={"fg": "white", "dim": True}
                    )
                else:
                    click.secho("--- start of {} ---".format(k), fg="white", dim=True)
                    click.secho(v, fg="white", dim=True)
                    click.secho("--- end of {} ---".format(k), fg="white", dim=True)

    def pprint_stack(self, stack, status=False):
        """Pretty print stack status"""
        # echo_pair('StackName', stack.stack_name)
        if status:
            echo_pair("Status", stack.stack_status, value_style=STACK_STATUS_TO_COLOR[stack.stack_status])

        if stack.stack_status == "STACK_NOT_FOUND":
            return

        echo_pair("StackID", stack.stack_id)
        # echo_pair('Description', stack.description)
        echo_pair("Created", stack.creation_time)
        if stack.last_updated_time:
            echo_pair("Last Updated", stack.last_updated_time)
        if stack.capabilities:
            echo_pair("Capabilities", ", ".join(stack.capabilities), value_style={"fg": "yellow"})
        echo_pair(
            "TerminationProtection",
            str(stack.enable_termination_protection),
            value_style={"fg": "red"} if stack.enable_termination_protection else None,
        )

        if stack.drift_information:
            drift_status = stack.drift_information["StackDriftStatus"]
            drift_timestamp = stack.drift_information.get("LastCheckTimestamp")
            echo_pair("Drift Status", drift_status, value_style=DRIFT_STATUS_TO_COLOR[drift_status])
            if drift_timestamp:
                echo_pair("Lasted Checked", drift_timestamp)
        else:
            echo_pair("Drift Status", "NOT_CHECKED")

    def pprint_stack_parameters(self, stack):
        if stack.parameters:
            echo_pair("Parameters")
            for p in stack.parameters:
                if "ResolvedValue" in p:
                    # SSM parameter
                    echo_pair("%s (%s)" % (p["ParameterKey"], p["ParameterValue"]), p["ResolvedValue"], indent=2)
                else:
                    echo_pair(p["ParameterKey"], p["ParameterValue"], indent=2)

        if stack.outputs:
            echo_pair("Outputs")
            for o in stack.outputs:
                echo_pair(o["OutputKey"], o["OutputValue"], indent=2)

        if stack.tags:
            echo_pair("Tags")
            for t in stack.tags:
                echo_pair(t["Key"], t["Value"], indent=2)

    def pprint_stack_resources(self, stack):
        echo_pair("Resources")

        for res in stack.resource_summaries.all():

            logical_id = res.logical_resource_id
            physical_id = res.physical_resource_id
            res_type = res.resource_type
            status = res.resource_status
            status_reason = res.resource_status_reason
            last_updated = res.last_updated_timestamp

            echo_pair("{} ({})".format(logical_id, res_type), indent=2)
            echo_pair("Physical ID", physical_id, indent=4)
            echo_pair("Last Updated", last_updated, indent=4)
            echo_pair("Status", status, value_style=STACK_STATUS_TO_COLOR[status], indent=4)
            if status_reason:
                echo_pair("Reason", status_reason, indent=6)
            if res.drift_information:
                drift_status = res.drift_information.get("StackResourceDriftStatus", "NOT_CHECKED")
                echo_pair("Drift Status", drift_status, value_style=DRIFT_STATUS_TO_COLOR[drift_status], indent=4)
                echo_pair("Lasted Checked", res.drift_information.get("LastCheckTimestamp", "unknown"), indent=6)

    def pprint_stack_exports(self, stack, session):
        client = session.client("cloudformation")
        echo_pair("Exports")
        for export in custom_paginator(client.list_exports, "Exports"):
            if export["ExportingStackId"] == stack.stack_id:
                echo_pair(export["Name"], export["Value"], indent=2)
                try:
                    for import_ in custom_paginator(client.list_imports, "Imports", ExportName=export["Name"]):
                        echo_pair("Imported By", import_, indent=4)
                except botocore.exceptions.ClientError as e:
                    pass

    def pprint_changeset(self, result, indent=0):
        changeset_name = result.get("ChangeSetName", "unknown")
        status = result["Status"]
        status_reason = result.get("StatusReason", None)

        echo_pair("ChangeSet Status", status, value_style=CHANGESET_STATUS_TO_COLOR[status], indent=indent)
        if status_reason:
            echo_pair("Status Reason", status_reason, indent=indent)

        if not result.get("Changes", []):
            return

        echo_pair("Resource Changes", indent=indent)
        for change in result["Changes"]:
            logical_id = change["ResourceChange"]["LogicalResourceId"]
            res_type = change["ResourceChange"]["ResourceType"]
            action = change["ResourceChange"]["Action"]
            replacement = change["ResourceChange"].get("Replacement", None)
            change_res_id = change["ResourceChange"].get("PhysicalResourceId", None)
            change_scope = change["ResourceChange"].get("Scope", None)
            change_details = {}
            for detail in change["ResourceChange"].get("Details", []):
                if detail["Target"].get("Path", None):
                    name = detail["Target"].get("Name", detail["Target"]["Path"])
                    if name not in change_details or detail["Evaluation"] == "Static":
                        change_details[name] = detail

            echo_pair("{} ({})".format(logical_id, res_type), indent=2 + indent)
            echo_pair("Action", action, value_style=CHANGESET_ACTION_TO_COLOR[action], indent=4 + indent)
            if replacement:
                echo_pair(
                    "Replacement",
                    replacement,
                    value_style=CHANGESET_REPLACEMENT_TO_COLOR[replacement],
                    indent=4 + indent,
                )
            if change_res_id:
                echo_pair("Physical Resource", change_res_id, indent=4 + indent)
            if change_scope:
                echo_pair("Change Scope", ",".join(change_scope), indent=4 + indent)
            if len(change_details):
                echo_pair("Changed Properties", "", indent=4 + indent)
                for k, v in change_details.items():
                    echo_pair(k, indent=6 + indent)
                    echo_pair(
                        "Requires Recreation",
                        v["Target"]["RequiresRecreation"],
                        value_style=CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR[v["Target"]["RequiresRecreation"]],
                        indent=8 + indent,
                    )
                    if v["Target"].get("Attribute", None):
                        echo_pair("Attribute Change Type", v["Target"]["Attribute"], indent=8 + indent)
                    if v.get("CausingEntity", None):
                        echo_pair("Causing Entity", v["CausingEntity"], indent=8 + indent)
                    if v.get("ChangeSource", None):
                        echo_pair("Change Source", v["ChangeSource"], indent=8 + indent)
                    if v["Target"].get("AfterValue", None):
                        echo_list(
                            "Value Change",
                            [
                                v["Target"].get("BeforeValue", "No Value"),
                                dict(fg=[76, 159, 158]),
                                " -> ",
                                None,
                                v["Target"]["AfterValue"],
                                dict(fg=[208, 240, 192]),
                            ],
                            indent=8 + indent,
                        )
            if res_type == "AWS::CloudFormation::Stack" and self.nested_changesets.get(
                f"{changeset_name}-{logical_id}", None
            ):
                echo_pair("Changeset for", logical_id, value_style=CHANGESET_ACTION_TO_COLOR[action], indent=4 + indent)
                self.pprint_changeset(self.nested_changesets[f"{changeset_name}-{logical_id}"], indent + 6)

    def pprint_stack_drift(self, drift):
        detection_status = drift["DetectionStatus"]
        drift_status = drift["StackDriftStatus"]
        drifted_resources = drift["DriftedStackResourceCount"]
        timestamp = drift["Timestamp"]

        echo_pair("Drift Detection Status", detection_status, value_style=DRIFT_STATUS_TO_COLOR[detection_status])
        echo_pair("Stack Drift Status", drift_status, value_style=DRIFT_STATUS_TO_COLOR[drift_status])
        echo_pair("Drifted resources", drifted_resources)
        echo_pair("Timestamp", timestamp)

    ## this is called per resource that has drifted
    def pprint_resource_drift(self, status):
        logical_id = status["LogicalResourceId"]
        res_type = status["ResourceType"]
        physical_id = status["PhysicalResourceId"]
        physical_resource_context = status.get("PhysicalResourceIdContext", [])
        drift_status = status["StackResourceDriftStatus"]
        timestamp = status["Timestamp"]

        echo_pair("{} ({})".format(logical_id, res_type), indent=2)
        echo_pair("Physical Id", physical_id, indent=4)
        for context in physical_resource_context:
            echo_pair(context["Key"], context["Value"], indent=4)
        echo_pair("Drift Status", drift_status, value_style=DRIFT_STATUS_TO_COLOR[drift_status], indent=4)
        echo_pair("Timestamp", timestamp, indent=4)

        if "PropertyDifferences" not in status or not status["PropertyDifferences"]:
            return

        echo_pair("Property Diff", ">", indent=4)
        for property in status["PropertyDifferences"]:
            echo_list(
                property["PropertyPath"],
                [
                    property.get("ExpectedValue", "Unknown"),
                    dict(fg=[76, 159, 158]),
                    " -> ",
                    None,
                    property.get("ActualValue", "Unknown"),
                    dict(fg=[208, 240, 192]),
                    f' ({property["DifferenceType"]})',
                    DRIFT_RESOURCE_TYPE_TO_COLOR[property["DifferenceType"]],
                ],
                indent=6,
            )

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.WaiterError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def wait_until_deploy_complete(self, session, stack, disable_tail_events=False, show_physical_resources=False):
        tail_thread = None
        if not disable_tail_events:
            tail_thread = start_tail_stack_events_daemon(
                session, stack, latest_events=0, show_physical_resources=show_physical_resources
            )

        try:
            waiter = session.client("cloudformation").get_waiter("stack_create_complete")
            waiter.wait(StackName=stack.stack_id)
        finally:
            if tail_thread:
                tail_thread.stop()

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.WaiterError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def wait_until_delete_complete(self, session, stack, show_physical_resources=False):
        ## test to ensure stack still exists before we wait and tail
        try:
            stack.load()
        except botocore.exceptions.ClientError as e:
            if not is_stack_does_not_exist_exception(e):
                click.echo(str(e))
            return

        tail_thread = start_tail_stack_events_daemon(session, stack, show_physical_resources=show_physical_resources)

        try:
            waiter = session.client("cloudformation").get_waiter("stack_delete_complete")
            waiter.wait(StackName=stack.stack_id)
        finally:
            if tail_thread:
                tail_thread.stop()

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.WaiterError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def wait_until_update_complete(self, session, stack, disable_tail_events=False, show_physical_resources=False):
        tail_thread = None
        if not disable_tail_events:
            tail_thread = start_tail_stack_events_daemon(
                session, stack, show_physical_resources=show_physical_resources
            )

        try:
            waiter = session.client("cloudformation").get_waiter("stack_update_complete")
            waiter.wait(StackName=stack.stack_id)
        finally:
            if tail_thread:
                tail_thread.stop()

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.WaiterError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def wait_until_changset_complete(self, client, changeset_id):
        waiter = client.get_waiter("change_set_create_complete")
        try:
            waiter.wait(ChangeSetName=changeset_id)
        except botocore.exceptions.WaiterError as e:
            if is_rate_limited_exception(e):
                # change set might be created successfully but we got throttling error, retry is needed so rerasing exception
                raise
            click.secho("ChangeSet create failed.", fg="red")
        else:
            click.secho("ChangeSet create complete.", fg="green")

    @backoff.on_exception(
        backoff.expo, botocore.exceptions.WaiterError, max_tries=10, giveup=is_not_rate_limited_exception
    )
    def fetch_nested_changesets(self, client, result):
        changeset_name = result.get("ChangeSetName", "unknown")
        for change in result["Changes"]:
            resource_type = change.get("ResourceChange", {}).get("ResourceType", "")
            logical_id = change.get("ResourceChange", {}).get("LogicalResourceId", "")
            if logical_id and resource_type == "AWS::CloudFormation::Stack":
                changeset_id = change.get("ResourceChange", {}).get("ChangeSetId", "")
                if changeset_id:
                    _id = f"{changeset_name}-{logical_id}"
                    ## Note we store based on combination of changeset ID and logical ID - as logical ID can be re-used
                    self.nested_changesets[_id] = describe_change_set(client, changeset_arn=changeset_id)
                    ## resursive to catch sub-stacks that themselves have sub-stacks
                    self.fetch_nested_changesets(client, self.nested_changesets[_id])
