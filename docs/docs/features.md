---
title: Features
weight: 15
---

# Features

## DRY Configuration

`cfn-cli` simplifies and reduces the overhead in configuring multiple CloudFormation stacks. Its single unified YAML based configuration encapsulates all needed configuration from stack name / region, stack parameters and tags, stack capabilities and polices.

Major sections of the configuration are **Blueprints** which typically define a given template and its required capabilities and polices and **Stages** which defined a collection of stacks that would typically define an entire AWS architecture for a given environment.

The `cfn-cli` YAML syntax allows for extensive re-use, to avoid duplicate configuration. The **Extends** keyword can be used on a stage (to inherit all configuration from an existing stage - useful for DR purposes) and on a stack within a stage, allowing a stack to inherit a previously defined Blueprints configuration.

## Ordered Stack Operations

`cfn-cli` allows for CloudFormation operations (deploy, update, delete etc) to be performed across a set of stages and stacks in a ordered fashion within a single CLI operation.

The CLI allows for a glob (wildcard) based selection of stages and stacks, each of which can be ordered within the configuration file - all stack operations then occur based on the order defined within the stage and then stack (ordering is reversed for delete operations).

Stages define the region and optional AWS profile required for the deployment operation, deployments across regions and accounts are possible within a single CLI operation.

## Packaging

`cfn-cli` will automatically find and package locally referenced resources within your CloudFormation templates is the configuration option `Package` is set to `True`. This vastly simplifies and reduces the amount of pre-processing required for CloudFormation deployments.  This effectively replaces the need to perform an `aws cloudformation package` pre-step on each template within a deployment.

By default resources are uploaded to a artifact s3 bucket. The default name for this bucket is `cfncli-${AWS_ACCOUNT_ID}-${AWS_REGION}`. If this bucket does not exist `cfn-cli` will attempt to create it.

> Note the S3 bucket name can be over-ridden via the use of the `--artifact-store` flag

The list of resource types that can be packaged by `cfn-cli` are:

| Resource Type                               | Property                                                     |
| ------------------------------------------- | ------------------------------------------------------------ |
| `AWS::Serverless::Function`                 | CodeUri                                                      |
| `AWS::Serverless::Api`                      | DefinitionUri                                                |
| `AWS::AppSync::GraphQLSchema`               | DefinitionS3Location                                         |
| `AWS::AppSync::Resolver`                    | RequestMappingTemplateS3Location, ResponseMappingTemplateS3Location |
| `AWS::AppSync::FunctionConfiguration`       | RequestMappingTemplateS3Location, ResponseMappingTemplateS3Location |
| `AWS::Lambda::Function`                     | Code                                                         |
| `AWS::ApiGateway::RestApi`                  | BodyS3Location                                               |
| `AWS::ElasticBeanstalk::ApplicationVersion` | SourceBundle                                                 |
| `AWS::Lambda::LayerVersion`                 | Content                                                      |
| `AWS::Serverless::LayerVersion`             | ContentUri                                                   |
| `AWS::ServerlessRepo::Application`          | ReadmeUrl, LicenseUrl                                        |
| `AWS::StepFunctions::StateMachine`          | DefinitionS3Location, DefinitionUri                          |
| `AWS::CloudFormation::Stack`                | TemplateURL                                                  |
| `AWS::Serverless::Application`              | Location                                                     |
| `AWS::CodeCommit::Repository`               | Code.S3                                                      |

In addition any `AWS::Include` used within a template (used for transforms) can also be packaged.

## Stack References

`cfn-cli` supports loosely coupled stack references i.e. without the use of AWS CloudFormation Imports (which causes a hard link and can mean the inability to update or delete resources that are linked to Outputs that have been Imported in other stacks)

Any output defined in a prior deployed stack can be referenced via: `${StageName.StackName.OutputName}`

These references work across AWS profiles (i.e. AWS accounts) and AWS Regions and as such are much more flexible than the in-built AWS CloudFormation Export/Import mechanism which are limited in use to within the same region and account 

## ChangeSet Support

`cfn-cli` supports producing and executing CloudFormation changesets both "singular" and nested (when using nested stacks). On production `cfn-cli` will pretty print the changeset, highlighting appropriately (red, amber, green) changes that will be applied and also highlighting the changed values when appropriate.

`cfn-cli` if used with the `--store` flag will save a `.cfncli-changeset` file containing the generated changeset ARNs for the stacks selected in the command, this file is then used when executing changesets, such that it can be guaranteed the changeset produced by `cfn-cli` is the one that is executed. 

If `cfn-cli` is to be used within a pipeline it is recommended to store the `.cfncli-changeset` file as a pipeline artifact for execution in future stages.