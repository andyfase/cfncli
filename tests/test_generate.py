"""Tests for generate command."""

import pytest
from cfncli.cli.main import cli
import os
import tempfile


def test_generate_config(cli_runner):
    """Test config file generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            result = cli_runner.invoke(cli, ["generate"])

            assert result.exit_code == 0
            assert os.path.exists("cfn-cli.yaml")

            # Check generated file content
            with open("cfn-cli.yaml", "r") as f:
                content = f.read()
                assert "Version: 3" in content
                assert "Stages:" in content
        finally:
            os.chdir(original_cwd)
