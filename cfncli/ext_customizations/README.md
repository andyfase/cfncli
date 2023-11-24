## External CloudFormation AWS CLI Dependencies

The code in this directory is directly copied from: https://github.com/aws/aws-cli/tree/develop/awscli/customizations minor modifications were made in the import statements which self reference the original code base or are wrappers to standard python libs. The original import remains commented out for clarity


Previous to this the codebase brought int the awscli package as a dependency, however that brings in issues with AWS CLI v2 which is no longer published too PyPi - see https://github.com/aws/aws-cli/issues/4947

The incompatibility of having a dependency on awscli v1 code with awscli v2 which is now used across cloudshell, cloud9 and any modern Amazon EC2 AMI makes the continued use of the v1 dependency untenable. Additionally as v2 is not on Pypi we cannot have a dependency on v2 - direct git dependencies are not allowed on pypi packages.

As such a decision was made to simply include the very small amount of awscli code that the overall aws-cli codebase is dependant on. This dependant code is small and very infrequently updated, as such the advantage of incorporating the code directly outweighs the benefit of continuing the dependency management.

By removing the dependency on the awscli pypi package https://pypi.org/project/awscli/ the cfn-cli package can co-exist nicely with all modern deployments of awscli, boto3 and botocore.