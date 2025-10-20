"""Tests for stack sync command."""

import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_stack_sync__new_stack_success(cli_runner, get_config):
    """Test successful stack sync."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        # Sync should deploy a new stack
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "sync"])
        assert result.exit_code == 0
        assert "Syncing stack" in result.output
        assert "Stack sync complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_stack_sync_success(cli_runner, get_config):
    """Test successful stack sync."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        # First deploy the stack
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Then sync to update the stack
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "sync"])
        assert result.exit_code == 0
        assert "Syncing stack" in result.output
        assert "Stack sync complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_stack_sync_with_options(cli_runner, get_config):
    """Test stack sync with various options."""
    tmpdir = get_config

    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        # First deploy the stack
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"], catch_exceptions=False
        )
        assert result.exit_code == 0

        # Then sync with options
        result = cli_runner.invoke(
            cli,
            ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "sync", "--no-wait"],
        )
        assert result.exit_code == 0
        assert "Syncing stack" in result.output
        assert "Stack sync complete" in result.output
    finally:
        os.chdir(original_cwd)
