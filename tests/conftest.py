"""Pytest configuration and shared fixtures."""
import pytest
import boto3
from moto import mock_aws
from click.testing import CliRunner
import tempfile
import os


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


@pytest.fixture
def sample_config():
    """Initial cfn-cli configuration."""
    return """
Version: 3

Stages:
  Test:
    TestStack:
      Template: test-template.yaml
      Region: us-east-1
      Parameters:
        BucketName: test-bucket
"""

@pytest.fixture
def sample_config_changed():
    """Initial cfn-cli configuration."""
    return """
Version: 3

Stages:
  Test:
    TestStack:
      Template: test-template.yaml
      Region: us-east-1
      Parameters:
        BucketName: test-bucket-changed
"""

@pytest.fixture
def sample_template():
    """Sample CloudFormation template."""
    return """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template
Parameters:
  BucketName:
    Type: String
Resources:
  TestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
Outputs:
  BucketName:
    Value: !Ref TestBucket
"""

@pytest.fixture
def sample_template_changed():
    """Sample CloudFormation template."""
    return """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template
Parameters:
  BucketName:
    Type: String
Resources:
  TestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${BucketName}-Foo"
Outputs:
  BucketName:
    Value: !Ref TestBucket
"""


@pytest.fixture
def temp_config_file(sample_config, sample_template):
    """Create temporary config and template files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "cfn-cli.yaml")
        template_path = os.path.join(tmpdir, "test-template.yaml")
        
        with open(config_path, "w") as f:
            f.write(sample_config)
        
        with open(template_path, "w") as f:
            f.write(sample_template)
        
        yield tmpdir, config_path, template_path

@pytest.fixture
def temp_config_file_changed(sample_config_changed, sample_template_changed):
    """Create temporary config and template files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "cfn-cli.yaml")
        template_path = os.path.join(tmpdir, "test-template.yaml")
        
        with open(config_path, "w") as f:
            f.write(sample_config_changed)
        
        with open(template_path, "w") as f:
            f.write(sample_template_changed)
        
        yield tmpdir, config_path, template_path