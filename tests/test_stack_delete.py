"""Tests for stack delete command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

import logging
logger = logging.getLogger(__name__)

@mock_aws
def test_stack_delete_success(cli_runner, get_config_single):
    """Test successful stack deletion."""
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
            "stack", "delete"
        ])
        
        assert result.exit_code == 0
        assert "Stack delete complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_delete_ignore_missing(cli_runner, get_config_single):
    """Test stack deletion with ignore missing option."""
    tmpdir = get_config_single
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "delete",
            "--ignore-missing"
        ])
        
        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)