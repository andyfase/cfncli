"""Tests for changeset pprint functionality."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from cfncli.cli.utils.pprint import StackPrettyPrinter
from cfncli.cli.utils.colormaps import RED, AMBER, GREEN
from tests.test_helpers import has_key_value_format, has_resource_format, has_indented_text
import logging

logger = logging.getLogger(__name__)


def test_pprint_changeset_no_changes():
    """Test changeset pretty printing with no changes."""

    mock_changeset_data = {
        "ChangeSetName": "empty-changeset",
        "Status": "FAILED",
        "StatusReason": "The submitted information didn't contain changes",
        "Changes": [],
    }

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        def capture_echo(*args, **kwargs):
            output_calls.append(("echo", args, kwargs))

        mock_secho.side_effect = capture_secho
        mock_echo.side_effect = capture_echo

        printer = StackPrettyPrinter()
        printer.pprint_changeset(mock_changeset_data)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Should show status with proper formatting but no resource changes
        assert has_key_value_format(all_lines, "ChangeSet Status", 0, "FAILED")
        assert has_key_value_format(all_lines, "Status Reason", 0, "The submitted information didn't contain changes")
        assert not has_key_value_format(all_lines, "Resource Changes", 0)


def test_pprint_changeset_nested_stack():
    """Test changeset pretty printing with nested stack changes."""

    mock_changeset_data = {
        "ChangeSetName": "parent-changeset",
        "Status": "CREATE_COMPLETE",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "NestedStack",
                    "ResourceType": "AWS::CloudFormation::Stack",
                    "Action": "Add",
                    "PhysicalResourceId": "nested-stack-123",
                }
            }
        ],
    }

    # Mock nested changeset data
    nested_changeset_data = {
        "ChangeSetName": "nested-changeset",
        "Status": "CREATE_COMPLETE",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "NestedResource",
                    "ResourceType": "AWS::S3::Bucket",
                    "Action": "Add",
                }
            }
        ],
    }

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        def capture_echo(*args, **kwargs):
            output_calls.append(("echo", args, kwargs))

        mock_secho.side_effect = capture_secho
        mock_echo.side_effect = capture_echo

        printer = StackPrettyPrinter()
        # Simulate nested changeset being stored
        printer.nested_changesets["parent-changeset-NestedStack"] = nested_changeset_data
        printer.pprint_changeset(mock_changeset_data)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Should show parent stack change with proper formatting
        assert has_resource_format(all_lines, "NestedStack", "AWS::CloudFormation::Stack", 2)
        assert has_key_value_format(all_lines, "Action", 4, "Add")

        # Should show nested changeset with proper formatting
        assert has_key_value_format(all_lines, "Changeset for", 4)
        assert any("NestedStack" in line for line in all_lines)
        assert has_resource_format(all_lines, "NestedResource", "AWS::S3::Bucket", 8)


def test_pprint_changeset_with_resource_changes():
    """Test changeset pretty printing with various resource changes and detailed property changes."""

    mock_changeset_data = {
        "ChangeSetName": "comprehensive-changeset",
        "Status": "CREATE_COMPLETE",
        "StatusReason": "Changeset created successfully",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "MyBucket",
                    "ResourceType": "AWS::S3::Bucket",
                    "Action": "Add",
                    "PhysicalResourceId": "my-test-bucket-123",
                    "Scope": ["Properties"],
                    "Details": [
                        {
                            "Target": {
                                "Name": "BucketName",
                                "Path": "/Properties/BucketName",
                                "RequiresRecreation": "Never",
                                "Attribute": "Properties",
                                "BeforeValue": None,
                                "AfterValue": "my-new-bucket",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                            "CausingEntity": "BucketName",
                        }
                    ],
                }
            },
            {
                "ResourceChange": {
                    "LogicalResourceId": "DetailedResource",
                    "ResourceType": "AWS::EC2::Instance",
                    "Action": "Modify",
                    "Replacement": "False",
                    "Scope": ["Properties"],
                    "Details": [
                        {
                            "Target": {
                                "Name": "InstanceType",
                                "Path": "/Properties/InstanceType",
                                "RequiresRecreation": "Never",
                                "Attribute": "Properties",
                                "BeforeValue": "t2.micro",
                                "AfterValue": "t3.small",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                            "CausingEntity": "InstanceType",
                        },
                        {
                            "Target": {
                                "Name": "SecurityGroups",
                                "Path": "/Properties/SecurityGroups",
                                "RequiresRecreation": "Always",
                            },
                            "Evaluation": "Dynamic",
                            "ChangeSource": "ParameterReference",
                            "CausingEntity": "SecurityGroupParameter",
                        },
                    ],
                }
            },
            {
                "ResourceChange": {
                    "LogicalResourceId": "MyFunction",
                    "ResourceType": "AWS::Lambda::Function",
                    "Action": "Remove",
                    "PhysicalResourceId": "my-function-789",
                }
            },
        ],
    }

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        def capture_echo(*args, **kwargs):
            output_calls.append(("echo", args, kwargs))

        mock_secho.side_effect = capture_secho
        mock_echo.side_effect = capture_echo

        printer = StackPrettyPrinter()
        printer.pprint_changeset(mock_changeset_data)

        # Verify proper formatting structure
        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Check changeset status formatting
        assert has_key_value_format(all_lines, "ChangeSet Status", 0, "CREATE_COMPLETE")
        assert has_key_value_format(all_lines, "Status Reason", 0, "Changeset created successfully")

        # Check resource changes formatting
        assert has_key_value_format(all_lines, "Resource Changes", 0)
        assert has_resource_format(all_lines, "MyBucket", "AWS::S3::Bucket", 2)
        assert has_key_value_format(all_lines, "Action", 4, "Add")

        assert has_resource_format(all_lines, "DetailedResource", "AWS::EC2::Instance", 2)
        assert has_key_value_format(all_lines, "Action", 4, "Modify")
        assert has_key_value_format(all_lines, "Replacement", 4, "False")

        assert has_resource_format(all_lines, "MyFunction", "AWS::Lambda::Function", 2)
        assert has_key_value_format(all_lines, "Action", 4, "Remove")

        # Check detailed property changes formatting
        assert has_key_value_format(all_lines, "Changed Properties", 4)
        assert has_key_value_format(all_lines, "BucketName", 6)
        assert has_key_value_format(all_lines, "InstanceType", 6)
        assert has_key_value_format(all_lines, "Requires Recreation", 8, "Never")
        assert has_key_value_format(all_lines, "Requires Recreation", 8, "Always")
        assert has_key_value_format(all_lines, "Causing Entity", 8, "InstanceType")
        assert has_key_value_format(all_lines, "Change Source", 8, "DirectModification")
        assert has_key_value_format(all_lines, "Change Source", 8, "ParameterReference")

        # Verify value change formatting with array syntax
        assert has_key_value_format(all_lines, "Value Change", 8, ["t2.micro", " -> ", "t3.small"])


def test_pprint_changeset_colors():
    """Test that changeset pretty printing applies correct colors."""

    mock_changeset_data = {
        "ChangeSetName": "color-test-changeset",
        "Status": "CREATE_COMPLETE",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "AddResource",
                    "ResourceType": "AWS::S3::Bucket",
                    "Action": "Add",
                    "Replacement": "True",
                    "Details": [{"Target": {"Name": "BucketName", "RequiresRecreation": "Always"}}],
                }
            },
            {
                "ResourceChange": {
                    "LogicalResourceId": "ModifyResource",
                    "ResourceType": "AWS::DynamoDB::Table",
                    "Action": "Modify",
                    "Replacement": "False",
                }
            },
            {
                "ResourceChange": {
                    "LogicalResourceId": "RemoveResource",
                    "ResourceType": "AWS::Lambda::Function",
                    "Action": "Remove",
                }
            },
        ],
    }

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        mock_secho.side_effect = capture_secho

        printer = StackPrettyPrinter()
        printer.pprint_changeset(mock_changeset_data)

        # Verify colors are applied correctly based on actual output
        # Check that CREATE_COMPLETE status has green color
        status_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "CREATE_COMPLETE"]
        assert len(status_calls) > 0
        assert status_calls[0][2]["fg"] == GREEN

        # Check action colors
        add_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Add"]
        modify_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Modify"]
        remove_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Remove"]

        assert len(add_calls) > 0 and add_calls[0][2]["fg"] == GREEN
        assert len(modify_calls) > 0 and modify_calls[0][2]["fg"] == AMBER
        assert len(remove_calls) > 0 and remove_calls[0][2]["fg"] == RED

        # Check replacement colors
        true_replacement_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "True"]
        false_replacement_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "False"]

        assert len(true_replacement_calls) > 0 and true_replacement_calls[0][2]["fg"] == RED
        assert len(false_replacement_calls) > 0 and false_replacement_calls[0][2]["fg"] == GREEN


def test_pprint_changeset_nested_with_colors():
    """Test nested changeset pretty printing with proper formatting and colors."""

    mock_changeset_data = {
        "ChangeSetName": "parent-changeset",
        "Status": "CREATE_COMPLETE",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "NestedStack",
                    "ResourceType": "AWS::CloudFormation::Stack",
                    "Action": "Add",
                    "PhysicalResourceId": "nested-stack-123",
                    "Scope": ["Properties"],
                }
            }
        ],
    }

    nested_changeset_data = {
        "ChangeSetName": "nested-changeset",
        "Status": "CREATE_COMPLETE",
        "Changes": [
            {
                "ResourceChange": {
                    "LogicalResourceId": "NestedBucket",
                    "ResourceType": "AWS::S3::Bucket",
                    "Action": "Modify",
                    "Replacement": "False",
                    "Details": [
                        {
                            "Target": {
                                "Name": "BucketName",
                                "Path": "/Properties/BucketName",
                                "RequiresRecreation": "Never",
                                "BeforeValue": "old-bucket",
                                "AfterValue": "new-bucket",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                            "CausingEntity": "BucketName",
                        }
                    ],
                }
            }
        ],
    }

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        def capture_echo(*args, **kwargs):
            output_calls.append(("echo", args, kwargs))

        mock_secho.side_effect = capture_secho
        mock_echo.side_effect = capture_echo

        printer = StackPrettyPrinter()
        printer.nested_changesets["parent-changeset-NestedStack"] = nested_changeset_data
        printer.pprint_changeset(mock_changeset_data)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Verify parent stack formatting
        assert has_resource_format(all_lines, "NestedStack", "AWS::CloudFormation::Stack", 2)
        assert has_key_value_format(all_lines, "Action", 4, "Add")
        assert has_key_value_format(all_lines, "Changeset for", 4, "NestedStack")

        # Verify nested stack formatting with proper indentation
        assert has_resource_format(all_lines, "NestedBucket", "AWS::S3::Bucket", 8)
        assert has_key_value_format(all_lines, "Action", 10, "Modify")
        assert has_key_value_format(all_lines, "Replacement", 10, "False")
        assert has_key_value_format(all_lines, "Changed Properties", 10)
        assert has_key_value_format(all_lines, "BucketName", 12)
        assert has_key_value_format(all_lines, "Requires Recreation", 14, "Never")
        assert has_key_value_format(all_lines, "Causing Entity", 14, "BucketName")
        assert has_key_value_format(all_lines, "Change Source", 14, "DirectModification")

        # Verify colors are applied correctly
        add_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Add"]
        modify_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Modify"]
        false_replacement_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "False"]
        never_recreation_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == "Never"]

        assert len(add_calls) > 0 and add_calls[0][2]["fg"] == GREEN
        assert len(modify_calls) > 0 and modify_calls[0][2]["fg"] == AMBER
        assert len(false_replacement_calls) > 0 and false_replacement_calls[0][2]["fg"] == GREEN
        assert len(never_recreation_calls) > 0 and never_recreation_calls[0][2]["fg"] == GREEN
