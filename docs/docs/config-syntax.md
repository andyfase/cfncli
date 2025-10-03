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

Blueprints are entirely optional. The syntax of a Blueprint and a Stack is effectively the same, however a Stack can **Extend** from an existing Blueprint where as a Blueprint does not support extending from other Blueprints

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
 DisableRollback: (boolean) flag to specify is rollback should be disabled
 TimeoutInMinutes: (int) value to specify max time for stack operation
 NotificationARNs: (array<string>) list of SNS ARNs for CloudFormation even notifications
 ResourceTypes: (array<string>) set of resources you opt-in to being able to create/update etc
 StackPolicy: (string) stack policy to apply to stack
	
```

`StackPolicy` possible values `ALLOW_ALL|ALLOW_MODIFY|DENY_DELETE|DENY_ALL`

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

The below 
