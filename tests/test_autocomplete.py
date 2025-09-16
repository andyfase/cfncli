"""Tests for autocomplete functionality."""

import pytest
import os
import logging
from cfncli.cli.main import cli
from click.shell_completion import BashComplete

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("get_config", ["autocomplete.yaml"], indirect=["get_config"])
def test_install_completion_bash(cli_runner, get_config):
    """Test that --install-completion generates bash completion script."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    # Mock SHELL environment variable
    original_shell = os.environ.get("SHELL")
    os.environ["SHELL"] = "/bin/bash"

    try:
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["--install-completion"])

        assert result.exit_code == 0
        assert "Add this to your bash profile:" in result.output
        assert "_cfn_cli_completion" in result.output
    finally:
        os.chdir(original_cwd)
        if original_shell:
            os.environ["SHELL"] = original_shell
        elif "SHELL" in os.environ:
            del os.environ["SHELL"]


def test_profile_autocomplete():
    """Test profile autocomplete function via Click's completion system."""
    import unittest.mock

    # Mock boto3 session to simulate available profiles
    mock_profiles = ["default", "development", "production", "staging"]

    with unittest.mock.patch("boto3.session.Session") as mock_session:
        mock_session.return_value.available_profiles = mock_profiles

        # Create completion context
        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")

        # Test profile option completion
        completions = comp.get_completions(["-p"], "")
        completion_values = [c.value for c in completions]

        # Should return the mocked profiles
        assert "default" in completion_values
        assert "development" in completion_values
        assert "production" in completion_values
        assert "staging" in completion_values

        # Test partial match
        partial_completions = comp.get_completions(["-p"], "dev")
        partial_values = [c.value for c in partial_completions]

        # Should only return profiles that start with "dev"
        assert "development" in partial_values
        assert "default" not in partial_values
        assert "production" not in partial_values


@pytest.mark.parametrize("get_config", ["autocomplete.yaml"], indirect=["get_config"])
def test_command_autocomplete(get_config):
    """Test completion via Click's shell completion system directly."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)

        # Create completion context
        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")

        # Test subcommand completion
        completions = comp.get_completions([], "s")
        completion_values = [c.value for c in completions]

        assert "stack" in completion_values
        assert "status" in completion_values
        assert "generate" not in completion_values

    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["autocomplete.yaml"], indirect=["get_config"])
def test_stage_autocomplete(get_config):
    """Test completion via Click's shell completion system directly."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)

        # Create completion context
        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")

        # Test stack option completion
        completions = comp.get_completions(["-s"], "Dev")
        completion_values = [c.value for c in completions]

        assert "Development.TestStack1" in completion_values
        assert "Development.NotTestStack2" in completion_values
        assert "Production.TestStack1" not in completion_values

    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["autocomplete.yaml"], indirect=["get_config"])
def test_stack_autocomplete(get_config):
    """Test completion via Click's shell completion system directly."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)

        # Create completion context
        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")

        # Test stack option completion
        completions = comp.get_completions(["-s"], "Development.Tes")
        completion_values = [c.value for c in completions]

        assert "Development.TestStack1" in completion_values
        assert "Development.NotTestStack2" not in completion_values
        assert "Production.TestStack1" not in completion_values

    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["autocomplete.yaml"], indirect=["get_config"])
def test_completion_source_generation(get_config):
    """Test that completion source can be generated."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        os.chdir(tmpdir)

        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")
        source = comp.source()

        # Should generate bash completion script
        assert "_cfn_cli_completion" in source
        assert "complete" in source

    finally:
        os.chdir(original_cwd)


def test_stack_completion_with_invalid_config():
    """Test stack completion handles invalid config gracefully."""
    original_cwd = os.getcwd()

    try:
        # Change to a directory with no config file
        os.chdir("/tmp")

        # Create completion context
        comp = BashComplete(cli, {}, "cfn-cli", "_CFN_CLI_COMPLETE")

        # Test stack option completion with no config file
        completions = comp.get_completions(["-s"], "")
        completion_values = [c.value for c in completions]

        # Should return empty list when no valid config is found
        assert completion_values == []

    finally:
        os.chdir(original_cwd)


def test_completion_with_unsupported_shell(cli_runner):
    """Test install completion with unsupported shell."""
    original_shell = os.environ.get("SHELL")
    os.environ["SHELL"] = "/bin/unsupported_shell"

    try:
        result = cli_runner.invoke(cli, ["--install-completion"])

        assert result.exit_code == 0
        assert "Unsupported shell: unsupported_shell" in result.output

    finally:
        if original_shell:
            os.environ["SHELL"] = original_shell
        elif "SHELL" in os.environ:
            del os.environ["SHELL"]
