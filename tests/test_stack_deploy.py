"""Tests for stack deploy command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
def test_stack_deploy_success(cli_runner, get_config_single):
    """Test successful stack deployment."""
    tmpdir = get_config_single
    
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
def test_stack_deploy_with_options(cli_runner, get_config_single):
    """Test stack deployment with various options."""
    tmpdir = get_config_single
    
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
        assert "Stack deployment complete" not in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
def test_stack_deploy_ignore_existing(cli_runner, get_config_single):
    """Test stack deployment with ignore existing option."""
    tmpdir = get_config_single
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy"
        ])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "stack", "deploy",
            "--ignore-existing"
        ])
        
        assert result.exit_code == 0
        assert "already exists" in result.output
    finally:
        os.chdir(original_cwd)