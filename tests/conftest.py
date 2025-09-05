"""Pytest configuration and shared fixtures."""
import pytest
import boto3
from moto import mock_aws
from click.testing import CliRunner
import tempfile
import os
import pathlib
import shutil
import logging
import unittest

config_file_name = 'cfn-cli.yaml'
config_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'resources', 'config')
template_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'resources', 'templates')

@pytest.fixture
def nolog_caplog(caplog: pytest.LogCaptureFixture):
    root = logging.getLogger()

    with unittest.mock.patch.object(root, 'disabled', new=False),\
        unittest.mock.patch.object(root, 'handlers', new=[]), \
        unittest.mock.patch.object(root, 'level', new=logging.NOTSET):
        yield caplog

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def cfn_client(aws_credentials):
    """Mock CloudFormation client."""
    with mock_aws():
        yield boto3.client("cloudformation", region_name="us-east-1")


@pytest.fixture
def s3_client(aws_credentials):
    """Mock S3 client."""
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def sts_client(aws_credentials):
    """Mock STS client."""
    with mock_aws():
        yield boto3.client("sts", region_name="us-east-1")


@pytest.fixture
def cli_runner():
    """Click CLI runner."""
    return CliRunner()

def read_file(dir, filename):
    with open(os.path.join(dir, filename)) as f:
        return f.read()
    
def write_file(dir, filename, content):
    with open(os.path.join(dir, filename), 'w') as f:
        return f.write(content)

@pytest.fixture
def config_single():
    return read_file(config_path, 'single.yaml')


#
# one fixture for each type of config, all templates copied across
#
@pytest.fixture
def get_config_single(config_single):
    with tempfile.TemporaryDirectory() as tmpdir:
        write_file(tmpdir, config_file_name, config_single)
        shutil.copytree(template_path, tmpdir, dirs_exist_ok=True)      
        yield tmpdir