"""Tests for stack delete command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

@mock_aws
def test_stack_delete_success(cli_runner, temp_config_file, cfn_client):
    """Test successful stack deletion."""
    tmpdir, config_path, template_path = temp_config_file
    
    # Create stack first
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
            "stack", "delete",
            "--no-wait"
        ])
        
        assert result.exit_code == 0
        assert "Deleting stack" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_delete_ignore_missing(cli_runner, temp_config_file):
    """Test stack deletion with ignore missing option."""
    tmpdir, config_path, template_path = temp_config_file
    
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