"""Tests for stack deploy command."""

import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os
import logging
import re

logger = logging.getLogger(__name__)


def generate_stack_regex(stacks):
    regex = ".*"
    for stack in stacks:
        regex += f"Deploying stack {stack}.*"
    return regex


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stack_order(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(generate_stack_regex(["NormalOrder1\.TestStack1", "NormalOrder1\.TestStack2"]), flags=re.DOTALL)
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "NormalOrder1.*", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stack_order_reverse(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(
        generate_stack_regex(["ReverseOrder1\.TestStack2", "ReverseOrder1\.TestStack1"]), flags=re.DOTALL
    )
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "ReverseOrder1.*", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_order(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(generate_stack_regex(["NormalOrder1\.TestStack1", "NormalOrder2\.TestStack1"]), flags=re.DOTALL)
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "NormalOrder*.TestStack1", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_order_reverse(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(
        generate_stack_regex(["ReverseOrder2\.TestStack1", "ReverseOrder1\.TestStack1"]), flags=re.DOTALL
    )
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "ReverseOrder*.TestStack1", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_and_stack_order(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(
        generate_stack_regex(
            [
                "NormalOrder1\.TestStack1",
                "NormalOrder1\.TestStack2",
                "NormalOrder2\.TestStack1",
                "NormalOrder2\.TestStack2",
            ]
        ),
        flags=re.DOTALL,
    )
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "NormalOrder*.*", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)


@pytest.mark.parametrize("get_config", ["multiple.yaml"], indirect=["get_config"])
@mock_aws
def test_stage_and_stack_order_reverse(cli_runner, get_config):
    """Test successful stack deployment."""
    tmpdir = get_config

    # Change to temp directory
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    regex = re.compile(
        generate_stack_regex(
            [
                "ReverseOrder2\.TestStack2",
                "ReverseOrder2\.TestStack1",
                "ReverseOrder1\.TestStack2",
                "ReverseOrder1\.TestStack1",
            ]
        ),
        flags=re.DOTALL,
    )
    try:
        result = cli_runner.invoke(cli, ["-f", "cfn-cli.yaml", "-s", "ReverseOrder*.*", "stack", "deploy"])
        assert result.exit_code == 0
        assert regex.match(result.output) is not None
    finally:
        os.chdir(original_cwd)
