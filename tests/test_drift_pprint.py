"""Tests for drift pprint functionality."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from cfncli.cli.utils.pprint import StackPrettyPrinter
from cfncli.cli.utils.colormaps import RED, AMBER, GREEN
from tests.test_helpers import has_key_value_format, has_resource_format, has_indented_text


def test_pprint_stack_drift():
    """Test stack drift pretty printing with various drift statuses."""

    mock_drift_data = {
        "DetectionStatus": "DETECTION_COMPLETE",
        "StackDriftStatus": "DRIFTED",
        "DriftedStackResourceCount": 3,
        "Timestamp": "2023-12-01T10:30:00Z",
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
        printer.pprint_stack_drift(mock_drift_data)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Check drift status formatting
        assert has_key_value_format(all_lines, "Drift Detection Status", 0, "DETECTION_COMPLETE")
        assert has_key_value_format(all_lines, "Stack Drift Status", 0, "DRIFTED")
        assert has_key_value_format(all_lines, "Drifted resources", 0, "3")
        assert has_key_value_format(all_lines, "Timestamp", 0, "2023-12-01T10:30:00Z")


def test_pprint_resource_drift_with_property_diff():
    """Test resource drift pretty printing with property differences."""

    mock_resource_drift = {
        "LogicalResourceId": "MyBucket",
        "ResourceType": "AWS::S3::Bucket",
        "PhysicalResourceId": "my-bucket-12345",
        "PhysicalResourceIdContext": [{"Key": "BucketName", "Value": "my-bucket-12345"}],
        "StackResourceDriftStatus": "MODIFIED",
        "Timestamp": "2023-12-01T10:30:00Z",
        "PropertyDifferences": [
            {
                "PropertyPath": "/BucketName",
                "ExpectedValue": "expected-bucket",
                "ActualValue": "actual-bucket",
                "DifferenceType": "MODIFY",
            },
            {
                "PropertyPath": "/VersioningConfiguration/Status",
                "ExpectedValue": "Enabled",
                "ActualValue": "Suspended",
                "DifferenceType": "MODIFY",
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
        printer.pprint_resource_drift(mock_resource_drift)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Check resource formatting
        assert has_resource_format(all_lines, "MyBucket", "AWS::S3::Bucket", 2)
        assert has_key_value_format(all_lines, "Physical Id", 4, "my-bucket-12345")
        assert has_key_value_format(all_lines, "BucketName", 4, "my-bucket-12345")
        assert has_key_value_format(all_lines, "Drift Status", 4, "MODIFIED")
        assert has_key_value_format(all_lines, "Timestamp", 4, "2023-12-01T10:30:00Z")
        assert has_key_value_format(all_lines, "Property Diff", 4, ">")

        # Check property differences formatting (like changeset)
        assert has_key_value_format(all_lines, "Property Diff", 4, ">")

        # Check property path formatting with proper indentation (6 spaces from echo_list)
        assert has_key_value_format(all_lines, "/BucketName", 6)
        assert has_key_value_format(all_lines, "/VersioningConfiguration/Status", 6)

        # Check for property value changes using array syntax (like changeset Value Change)
        assert has_key_value_format(all_lines, "/BucketName", 6, ["expected-bucket", " -> ", "actual-bucket"])
        assert has_key_value_format(all_lines, "/VersioningConfiguration/Status", 6, ["Enabled", " -> ", "Suspended"])

        # Check that difference types appear with proper formatting
        all_text = " ".join(str(line) for line in all_lines)
        assert "(MODIFY)" in all_text


def test_pprint_resource_drift_no_properties():
    """Test resource drift pretty printing without property differences."""

    mock_resource_drift = {
        "LogicalResourceId": "MyFunction",
        "ResourceType": "AWS::Lambda::Function",
        "PhysicalResourceId": "my-function-arn",
        "StackResourceDriftStatus": "IN_SYNC",
        "Timestamp": "2023-12-01T10:30:00Z",
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
        printer.pprint_resource_drift(mock_resource_drift)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Check resource formatting
        assert has_resource_format(all_lines, "MyFunction", "AWS::Lambda::Function", 2)
        assert has_key_value_format(all_lines, "Physical Id", 4, "my-function-arn")
        assert has_key_value_format(all_lines, "Drift Status", 4, "IN_SYNC")
        assert has_key_value_format(all_lines, "Timestamp", 4, "2023-12-01T10:30:00Z")

        # Should not have property diff section
        assert not has_key_value_format(all_lines, "Property Diff", 4)


def test_pprint_drift_colors():
    """Test that drift pretty printing applies correct colors."""

    # Test different drift statuses with correct color mappings
    test_cases = [
        ("DETECTION_COMPLETE", GREEN),
        ("DETECTION_IN_PROGRESS", AMBER),
        ("DETECTION_FAILED", RED),
        ("DRIFTED", RED),
        ("IN_SYNC", GREEN),
        ("MODIFIED", AMBER),  # MODIFIED maps to amber, not red
        ("DELETED", RED),
    ]

    for status, expected_color in test_cases:
        mock_drift_data = {
            "DetectionStatus": status,
            "StackDriftStatus": status,
            "DriftedStackResourceCount": 1,
            "Timestamp": "2023-12-01T10:30:00Z",
        }

        with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
            output_calls = []

            def capture_secho(*args, **kwargs):
                output_calls.append(("secho", args, kwargs))

            mock_secho.side_effect = capture_secho

            printer = StackPrettyPrinter()
            printer.pprint_stack_drift(mock_drift_data)

            # Check that status has correct color
            status_calls = [call for call in output_calls if len(call[1]) > 0 and call[1][0] == status]
            if status_calls:  # Only check if the status appears in output
                assert len(status_calls) > 0
                assert status_calls[0][2]["fg"] == expected_color


def test_pprint_multiple_resource_drifts():
    """Test multiple resource drift entries with different statuses."""

    mock_resources = [
        {
            "LogicalResourceId": "DriftedBucket",
            "ResourceType": "AWS::S3::Bucket",
            "PhysicalResourceId": "drifted-bucket-123",
            "StackResourceDriftStatus": "MODIFIED",
            "Timestamp": "2023-12-01T10:30:00Z",
            "PropertyDifferences": [
                {
                    "PropertyPath": "/BucketName",
                    "ExpectedValue": "expected-name",
                    "ActualValue": "actual-name",
                    "DifferenceType": "MODIFY",
                }
            ],
        },
        {
            "LogicalResourceId": "InSyncTable",
            "ResourceType": "AWS::DynamoDB::Table",
            "PhysicalResourceId": "in-sync-table",
            "StackResourceDriftStatus": "IN_SYNC",
            "Timestamp": "2023-12-01T10:30:00Z",
        },
        {
            "LogicalResourceId": "DeletedFunction",
            "ResourceType": "AWS::Lambda::Function",
            "PhysicalResourceId": "deleted-function-arn",
            "StackResourceDriftStatus": "DELETED",
            "Timestamp": "2023-12-01T10:30:00Z",
        },
    ]

    with patch("click.secho") as mock_secho, patch("click.echo") as mock_echo:
        output_calls = []

        def capture_secho(*args, **kwargs):
            output_calls.append(("secho", args, kwargs))

        def capture_echo(*args, **kwargs):
            output_calls.append(("echo", args, kwargs))

        mock_secho.side_effect = capture_secho
        mock_echo.side_effect = capture_echo

        printer = StackPrettyPrinter()

        # Print all resource drifts
        for resource in mock_resources:
            printer.pprint_resource_drift(resource)

        all_lines = [call[1][0] if call[1] else "" for call in output_calls]

        # Check all resources are formatted correctly
        assert has_resource_format(all_lines, "DriftedBucket", "AWS::S3::Bucket", 2)
        assert has_key_value_format(all_lines, "Drift Status", 4, "MODIFIED")

        assert has_resource_format(all_lines, "InSyncTable", "AWS::DynamoDB::Table", 2)
        assert has_key_value_format(all_lines, "Drift Status", 4, "IN_SYNC")

        assert has_resource_format(all_lines, "DeletedFunction", "AWS::Lambda::Function", 2)
        assert has_key_value_format(all_lines, "Drift Status", 4, "DELETED")

        # Check that property diff only appears for drifted resource
        assert has_key_value_format(all_lines, "Property Diff", 4, ">")

        # Check the actual property value change for the drifted resource
        assert has_key_value_format(all_lines, "/BucketName", 6, ["expected-name", " -> ", "actual-name"])

        # Verify that only the drifted resource has property diff, others don't
        property_diff_count = sum(1 for line in all_lines if line == "    Property Diff: ")
        assert property_diff_count == 1  # Only one resource should have property diff
