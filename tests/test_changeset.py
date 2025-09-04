"""Tests for changeset commands."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os
from .test_stack_deploy import test_stack_deploy_success

import logging
logger = logging.getLogger(__name__)


@mock_aws
def test_changeset_create_new_stack(cli_runner, temp_config_file):
    """Test changeset creation for new stack."""
    tmpdir, config_path, template_path = temp_config_file
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "changeset", "create"
        ])
        print(result)
        assert result.exit_code == 0
        assert "Generating Changeset for stack" in result.output
        assert "ChangeSet Type" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_changeset_create_existing_stack(cli_runner, temp_config_file, temp_config_file_changed):
    """Test changeset creation for existing stack with parameter change."""
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
        
        # Create changeset with changed parameters
        os.chdir(tmpdir_changed)
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "changeset", "create"
        ])

        assert result.exit_code == 0
        assert "ChangeSet creation complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_changeset_create_disable_nested(cli_runner, temp_config_file):
    """Test changeset creation with nested disabled."""
    tmpdir, config_path, template_path = temp_config_file
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "changeset", "create",
            "--disable-nested"
        ])
        
        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)