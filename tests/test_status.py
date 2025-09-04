"""Tests for status command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os

@mock_aws
def test_status_existing_stack(cli_runner, temp_config_file, cfn_client):
    """Test status command for existing stack."""
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
            "status"
        ])
        
        assert result.exit_code == 0
        assert "TestStack" in result.output
    finally:
        os.chdir(original_cwd)

@mock_aws
def test_status_with_resources(cli_runner, temp_config_file, cfn_client, monkeypatch):
    """Test status command with resources flag."""
    tmpdir, config_path, template_path = temp_config_file
    
    # Create stack first
    with open(template_path, 'r') as f:
        template_body = f.read()
    
    cfn_client.create_stack(
        StackName="TestStack",
        TemplateBody=template_body,
        Parameters=[{"ParameterKey": "BucketName", "ParameterValue": "test-bucket"}]
    )
    
    # Mock resource_summaries.all() to prevent hanging with moto
    def mock_resource_summaries_all(self):
        # Return empty list to avoid hanging iteration
        return []
    
    # Patch the resource_summaries.all method
    import boto3.resources.collection
    monkeypatch.setattr(boto3.resources.collection.ResourceCollection, "all", mock_resource_summaries_all)
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "status",
            "-r"
        ])
        
        assert result.exit_code == 0
        assert "Resources" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_status_nonexistent_stack(cli_runner, temp_config_file):
    """Test status command for non-existent stack."""
    tmpdir, config_path, template_path = temp_config_file
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "status"
        ])
        
        
        assert result.exit_code == 0
        assert "STACK_NOT_FOUND" in result.output
    finally:
        os.chdir(original_cwd)