"""Tests for stack update command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

import logging
logger = logging.getLogger(__name__)


@mock_aws
def test_stack_update_success(cli_runner, temp_config_file, temp_config_file_changed):
    """Test successful stack update."""
    tmpdir, _config_path, _template_path = temp_config_file
    tmpdir_changed, _config_path_changed, _template_path_changed = temp_config_file_changed
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
    
        os.chdir(tmpdir_changed)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "update",
        ])
        assert result.exit_code == 0
        assert "Stack update complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_update_use_previous_template(cli_runner, temp_config_file, temp_config_file_changed):
    """Test stack update with previous template."""
    tmpdir, _config_path, _template_path = temp_config_file
    tmpdir_changed, _config_path_changed, _template_path_changed = temp_config_file_changed
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
    
        os.chdir(tmpdir_changed)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "update",
            "--use-previous-template"
        ])      
        assert result.exit_code == 0
        assert "Stack update complete" in result.output
    finally:
        os.chdir(original_cwd)