"""Tests for drift detection commands."""
import pytest
from moto import mock_aws
from cfncli.cli.main import cli
import os



## Note Tests currently disabled - drift commands via MOTO are not yet supported
## See https://github.com/getmoto/moto/blob/master/IMPLEMENTATION_COVERAGE.md

# @mock_aws
# def test_drift_detect(cli_runner, temp_config_file, cfn_client):
#     """Test drift detection command."""
#     tmpdir, config_path, template_path = temp_config_file
    
#     # Create stack first
#     with open(template_path, 'r') as f:
#         template_body = f.read()
    
#     cfn_client.create_stack(
#         StackName="TestStack",
#         TemplateBody=template_body,
#         Parameters=[{"ParameterKey": "BucketName", "ParameterValue": "test-bucket"}]
#     )
    
#     original_cwd = os.getcwd()
#     os.chdir(tmpdir)
    
#     try:
#         result = cli_runner.invoke(cli, [
#             "-f", "cfn-cli.yaml",
#             "-s", "Test.TestStack",
#             "drift", "detect"
#         ])
        
#         assert result.exit_code == 0
#         assert "Detecting drift for stack" in result.output
#     finally:
#         os.chdir(original_cwd)


# @mock_aws
# def test_drift_diff(cli_runner, temp_config_file, cfn_client):
#     """Test drift diff command."""
#     tmpdir, config_path, template_path = temp_config_file
    
#     # Create stack first
#     with open(template_path, 'r') as f:
#         template_body = f.read()
    
#     cfn_client.create_stack(
#         StackName="TestStack",
#         TemplateBody=template_body,
#         Parameters=[{"ParameterKey": "BucketName", "ParameterValue": "test-bucket"}]
#     )
    
#     original_cwd = os.getcwd()
#     os.chdir(tmpdir)
    
#     try:
#         result = cli_runner.invoke(cli, [
#             "-f", "cfn-cli.yaml",
#             "-s", "Test.TestStack",
#             "drift", "diff"
#         ])
        
#         assert result.exit_code == 0
#     finally:
#         os.chdir(original_cwd)