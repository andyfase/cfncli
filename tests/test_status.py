"""Tests for status command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

@mock_aws
def test_status_existing_stack(cli_runner, get_config_single):
    """Test status command for existing stack."""
    tmpdir = get_config_single
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)
        # Create initial stack
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "status"
        ])
        
        assert result.exit_code == 0
        assert "TestStack" in result.output
    finally:
        os.chdir(original_cwd)

@mock_aws
def test_status_with_resources(cli_runner, get_config_single):
    """Test status command with resources flag."""
    tmpdir = get_config_single
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)
        # Create initial stack
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "status",
            "-r"
        ])
        
        assert result.exit_code == 0
        assert "Resources" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_status_nonexistent_stack(cli_runner, get_config_single):
    """Test status command for non-existent stack."""
    tmpdir = get_config_single    
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "status"
        ])

        assert result.exit_code == 0
        assert "STACK_NOT_FOUND" in result.output
    finally:
        os.chdir(original_cwd)