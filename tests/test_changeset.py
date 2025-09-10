"""Tests for changeset commands."""

import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

import logging

logger = logging.getLogger(__name__)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_changeset_create_new_stack(cli_runner, get_config):
    """Test changeset creation for new stack."""
    tmpdir = get_config
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "changeset", "create"])
        print(result)
        assert result.exit_code == 0
        assert "Generating Changeset for stack" in result.output
        assert "ChangeSet Type" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_changeset_create_existing_stack(cli_runner, get_config):
    """Test changeset creation for existing stack with parameter change."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Create changeset with changed parameters
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "create"]
        )

        assert result.exit_code == 0
        assert "ChangeSet creation complete" in result.output
    finally:
        os.chdir(original_cwd)


# nolog_caplog - used to prevent pytest inferering with logging from click on error cases
@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_changeset_create_fails_no_change(cli_runner, get_config, nolog_caplog):
    """Test changeset creation for existing stack with parameter change."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Create changeset with changed parameters
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "changeset", "create"], catch_exceptions=False
        )

        assert result.exit_code == 1
        logger.error(result.stdout)
        assert "contains no updates" in result.stdout
    finally:
        os.chdir(original_cwd)


# nolog_caplog - used to prevent pytest inferering with logging from click on error cases
@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_changeset_create_fails_no_change_skip(cli_runner, get_config, nolog_caplog):
    """Test changeset creation for existing stack with parameter change."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Create changeset with changed parameters
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "changeset", "create", "-i"]
        )

        assert result.exit_code == 0
        assert "contains no updates" in result.stdout
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_changeset_create_disable_nested(cli_runner, get_config):
    """Test changeset creation with nested disabled."""
    tmpdir = get_config

    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(
            cli,
            ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "create", "--disable-nested"],
        )

        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_exec_changeset(cli_runner, get_config):
    """Test changeset creation for existing stack with parameter change."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Create changeset with changed parameters
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "create", "--store"]
        )

        assert result.exit_code == 0
        assert "ChangeSet creation complete" in result.output

        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "exec"]
        )

        assert result.exit_code == 0
        assert "ChangeSet execution complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_exec_changeset_no_store(cli_runner, get_config):
    """Test changeset creation for existing stack with parameter change."""
    tmpdir = get_config
    original_cwd = os.getcwd()

    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "stack", "deploy"])
        assert result.exit_code == 0

        # Create changeset with changed parameters
        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "create"]
        )

        assert result.exit_code == 0
        assert "ChangeSet creation complete" in result.output

        result = cli_runner.invoke(
            cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStackChanged", "stack", "changeset", "exec"]
        )

        # assert result.exit_code == 1
        assert "ChangeSet file .cfn-cli-changesets does not exist" in result.output
    finally:
        os.chdir(original_cwd)
