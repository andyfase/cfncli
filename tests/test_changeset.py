"""Tests for changeset commands."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


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
        
        assert result.exit_code == 0
        assert "Generating Changeset for stack" in result.output
        assert "ChangeSet Type" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_changeset_create_existing_stack(cli_runner, temp_config_file, cfn_client):
    """Test changeset creation for existing stack."""
    tmpdir, config_path, template_path = temp_config_file
    
    # Create initial stack
    with open(template_path, 'r') as f:
        template_body = f.read()
    
    cfn_client.create_stack(
        StackName="TestStack",
        TemplateBody=template_body,
        Parameters=[{"ParameterKey": "BucketName", "ParameterValue": "test-bucket"}]
    )
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "changeset", "create",
            "--use-previous-template"
        ])
        
        assert result.exit_code == 0
        assert "Generating Changeset for stack" in result.output
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