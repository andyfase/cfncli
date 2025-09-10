"""Tests for stack deploy command."""

import pytest
from moto import mock_aws
from moto.core import set_initial_no_auth_action_count
from cfncli.cli.main import cli
import os
import logging

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("get_config", ["lambda.yaml"], indirect=["get_config"])
@mock_aws
def test_package_deploy_success(cli_runner, get_config, setenv_test_runner):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.LambdaPackagedStack", "stack", "deploy"])
        assert result.exit_code == 0
        assert "Successfully packaged artifacts and uploaded to s3" in result.output
        assert "Stack deployment complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["lambda.yaml"], indirect=["get_config"])
def test_package_update_success(cli_runner, get_config, setenv_test_runner):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.LambdaPackagedStack", "stack", "deploy"])
        assert result.exit_code == 0
        assert "Packaged" in result.output
        assert "Deploying stack" in result.output
        assert "Stack deployment complete" in result.output

        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.LambdaPackagedStack", "stack", "update"])
        assert result.exit_code == 0
        assert "Successfully packaged artifacts and uploaded to s3" in result.output
        assert "Stack update complete" in result.output
    finally:
        os.chdir(original_cwd)
