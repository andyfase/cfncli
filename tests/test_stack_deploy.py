"""Tests for stack deploy command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
def test_stack_deploy_success(cli_runner, temp_config_file):
    """Test successful stack deployment."""
    tmpdir, config_path, template_path = temp_config_file
    
    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        
        assert result.exit_code == 0
        assert "Deploying stack" in result.output
        assert "Stack deployment complete" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_deploy_with_options(cli_runner, temp_config_file):
    """Test stack deployment with various options."""
    tmpdir, config_path, template_path = temp_config_file
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy",
            "--no-wait",
            "--disable-rollback",
            "--timeout-in-minutes", "30",
            "--on-failure", "DELETE"
        ])
        
        assert result.exit_code == 0
        assert "Deploying stack" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_deploy_ignore_existing(cli_runner, temp_config_file, cfn_client):
    """Test stack deployment with ignore existing option."""
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
            "stack", "deploy",
            "--ignore-existing"
        ])
        
        assert result.exit_code == 0
    finally:
        os.chdir(original_cwd)