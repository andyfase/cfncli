"""Tests for stack deploy command."""

import pytest
from moto import mock_aws
from moto.core import set_initial_no_auth_action_count
from cfncli.cli.main import cli
import os
import logging

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("get_config", ["config-options.yaml"], indirect=["get_config"])
@mock_aws
def test_invalid_account(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "IncorrectAccount.TestStack", "stack", "deploy"])
        assert result.exit_code == 1
        assert "Incorrect Account Detected!" in result.output
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["config-options.yaml"], indirect=["get_config"])
@mock_aws
def test_region_override(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "USEastRegion.TestStack", "stack", "deploy"])
        assert result.exit_code == 0
        assert "us-east-1" in result.output
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["config-options.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_extend(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Extended.TestStack", "stack", "deploy"])
        assert result.exit_code == 0
        assert "Deploying stack Extended.TestStack" in result.output
        assert "Stack deployment complete" in result.output
        assert "stack/test-bucket" in result.output
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["config-options.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_extend_merge(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "ExtendedMerge.TestStack", "stack", "deploy"])
        logger.error(result)
        logger.error(result.output)
        assert result.exit_code == 0
        assert "Deploying stack ExtendedMerge.TestStack" in result.output
        assert "Stack deployment complete" in result.output
        assert "stack/different-bucket" in result.output
    finally:
        os.chdir(original_cwd)
