---
title: Configuration File
weight: 20
---

# Configuration File Syntax

The codebase contains a JSONSchema definition of the required configuration file. This section of the docs describes the use and purpose of the options available.

## Overview

The general breakdown of the `cfn-cli.yaml` configuration file is

```yaml
Version: 3
Blueprints:
 blueprint1:
  ... blueprint configuration options
Stages:
 stage1:
  Config:
   ... stage configuration options
   ... series of stacks
  stage2:
   ... etc
```

Blueprints are entirely optional. The syntax of a Blueprint and a Stack is effectively the same, however a Stack can **Extend** from an existing Blueprint whereas a Blueprint does not support extending from other Blueprints

## Blueprint / Stack

A Blueprint or Stack  has the following settings

```yaml
blueprint-stack:
 ## mandatory settings
 Order: (int) the order of the stack in deployment
 Template: (string) the path to the CloudFormation template file
 StackPolicy: (string) reference to a support canned stack policy 
 Capabilities: (array<string>) set of stack capabilities required for the stack
 StackName: (string) name of stack to deploy
 Region: (string) AWS region to deploy in
	
 ## optional settings
 Extend: (string) [Stack Only] reference to the blueprint to extend from	 
 Parameters: (dict) Set of key/value parameters used for the stack in question
 Profile: (string) optional AWS profile to assume before deployment
 Package: (boolean) Flag to specify if cfn-cli should attempt packaging
 RoleARN: (string) CloudFormation deployment role to use
 Tags: (dict) set of tag key/values to apply to stack and all resources deployed via stack
 EnableTerminationProtection: (boolean) flag to indicate if stack termination protection should be set on stack
 DisableRollback: (boolean) flag to specify if rollback should be disabled
 TimeoutInMinutes: (int) value to specify max time for stack operation
 NotificationARNs: (array<string>) list of SNS ARNs for CloudFormation event notifications
 ResourceTypes: (array<string>) set of resources you opt-in to being able to create/update etc
 StackPolicy: (string) stack policy to apply to stack
	
```

`StackPolicy` possible values `ALLOW_ALL | ALLOW_MODIFY | DENY_DELETE | DENY_ALL`

`Capabilities` possible values: `CAPABILITY_IAM | CAPABILITY_NAMED_IAM | CAPABILITY_AUTO_EXPAND`

## Stage Options

A stage has a `Config` object and a series of stacks (for which the options are defined above)

```yaml
stage:
 Config:
  ## all options are optional
  Extend: (string) Reference to a stage to extend all other config and stacks from
  Account: (string) Reference to a AWS account number that must be used for deployment
  RoleARN: (string) CloudFormation deployment role to use for all stacks in stage (can be overridden)
  Region: (string) AWS region to use for all stacks in stage (can be overridden)
  StackPrefix: (string) Prefix to be applied to the name of every stack within the stage
  Tags: (dict) Set of tag key/values to apply to stacks within the stage
  Parameters: (dict) Set of key/value parameters to add to all stacks within the stage
```

## Reference Example

The below example complete `cfn-cli.yaml`configuration is an annotated reference of what is possible. This configuration deploys a `bucket` and `lambda` stack within the production environment and just a `lambda` stack in the disaster recovery region, as the lambda stack will re-use the bucket from production.

It's a good demonstration of **extending** both from Blueprints and from Stages, the ability to use stack exports across regions (without a hard dependency via CloudFormation imports) and finally the use of **packaging** for our lambda stack which will automatically package and zip our lambda code on deployment.

```yaml
Version: 3

## Start with blueprints for common stack settings that can be re-used across stages
Blueprints:
  BpBucket: 
    Order: 1
    Template: ./templates/bucket.yaml
    StackPolicy: ALLOW_ALL
    Capabilities: [CAPABILITY_IAM]
    StackName: "bucket"
    Parameters:
      BucketSuffix: cfncli

  BpLambda:
    Order: 2
    Template: ./templates/lambda.yaml
    StackPolicy: ALLOW_ALL
    Capabilities: [CAPABILITY_IAM]
    StackName: "lambda"
    Package:  true
    Parameters:
      LambdaMemory: 256
      LambdaTimeout: 600

## now define our stages
Stages:
  prod:
    Config:
      Extends: dr ## We bring in all config and stacks from dr stage
      Account: "987654321" ## lock stage to a specific account number
      Order: 1 ## set Order to before DR
      Region: "us-west-2" ## override region
      StackPrefix: 'prod-' ## override prefix
      Tags:
      	## we already get the Team tag so just override the DR tag
        DR: "False" 
      Parameters:
        Environment: "prod" ## override environment param for entire stage
    bucket:
      Extends: BpBucket
      Parameters:
         isDr: "False"
    lambda:
    	## no need for Extends here as we already got this stage from extending the entire dr stage
      Parameters:
        LambdaMemory: 1024
        LambdaTimeout: 600
  dr:
    Config:
      Order: 2 ## DR stage goes last as we use a stack reference from our prod stage
      Account: "123456789" ## lock stage to a specific account number
      Region: "us-east-1"
      StackPrefix: 'dr-' ## set a stack prefix so we dont need to rename stacks between stages
      Tags:
        DR: "True"
        Team: "SuperSecDevOps"
      Parameters:
        Application: "superapp"
        Environment: "dr"
    lambda:
      Extends: BpLambda
      Parameters:
        BucketName: ${prod.bucket.BucketName} ## taken from prod stage, no hard linking!
```



The output of this will be, in production:

> Stack **prod-bucket** deployed in **us-west-2** with a output **BucketName**
>
> Stack **prod-lambda** deployed in **us-west-2** using the **BucketName** export from the **prod-bucket** stack

And in dev:

> Stack **dev-lambda** deployed in **us-east-1** using the **BucketName** export from the **prod-bucket** stack from **us-west-2**

