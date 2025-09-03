"""Tests for stack update command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
def test_stack_update_success(cli_runner, temp_config_file, cfn_client):
    """Test successful stack update."""
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
            "stack", "update",
            "--no-wait"
        ])
        
        assert result.exit_code == 0
        assert "Updating stack" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_update_use_previous_template(cli_runner, temp_config_file, cfn_client):
    """Test stack update with previous template."""
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
            "stack", "update",
            "--use-previous-template",
            "--no-wait"
        ])
        
        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)