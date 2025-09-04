"""Tests for validate command."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
def test_validate_template(cli_runner, temp_config_file):
    """Test template validation."""
    tmpdir, config_path, template_path = temp_config_file
    
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    
    try:
        result = cli_runner.invoke(cli, [
            "-f", "cfn-cli.yaml",
            "-s", "Test.TestStack",
            "validate"
        ])
        
        assert result.exit_code == 0
        assert "Validation complete" in result.output
    finally:
        os.chdir(original_cwd)