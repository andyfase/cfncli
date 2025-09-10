"""Tests for stack update command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

import logging
logger = logging.getLogger(__name__)


@mock_aws
@pytest.mark.parametrize('get_config', ['single.yaml'], indirect=['get_config'])
def test_stack_update_success(cli_runner, get_config):
    """Test successful stack update."""
    tmpdir = get_config
    original_cwd = os.getcwd()
    
    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        assert result.exit_code == 0
    
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStackChanged",
            "stack", "update",
        ])
        assert result.exit_code == 0
        assert "Stack update complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize('get_config', ['single.yaml'], indirect=['get_config'])
def test_stack_update_use_previous_template(cli_runner, get_config):
    """Test stack update with previous template."""
    tmpdir = get_config
    original_cwd = os.getcwd()
    
    try:
        # Create initial stack
        os.chdir(tmpdir)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        assert result.exit_code == 0
    
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStackChanged",
            "stack", "update",
            "--use-previous-template"
        ])      
        assert result.exit_code == 0
        assert "Stack update complete" in result.output
    finally:
        os.chdir(original_cwd)