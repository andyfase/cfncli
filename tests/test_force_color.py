"""Tests for FORCE_COLOR environment variable."""

import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_force_color_true(cli_runner, get_config, monkeypatch):
    """Test that FORCE_COLOR=true enables color output."""
    monkeypatch.setenv("FORCE_COLOR", "true")
    tmpdir = get_config

    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "validate"], color=False)
        assert result.exit_code == 0
        # Check that ANSI color codes are present even when color=False due to FORCE_COLOR
        assert "\x1b[" in result.output
    finally:
        os.chdir(original_cwd)


@mock_aws
@pytest.mark.parametrize("get_config", ["single.yaml"], indirect=["get_config"])
def test_force_color_false(cli_runner, get_config, monkeypatch):
    """Test that FORCE_COLOR=false does not enable color output."""
    monkeypatch.setenv("FORCE_COLOR", "false")
    tmpdir = get_config

    original_cwd = os.getcwd()
    os.chdir(tmpdir)

    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "Test.TestStack", "validate"], color=False)
        assert result.exit_code == 0
        # Check that no ANSI color codes are present
        # the automatic detection should fail in our test runner as clicks detection will not find a valid tty
        assert "\x1b[" not in result.output
    finally:
        os.chdir(original_cwd)
