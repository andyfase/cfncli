---
title: Getting Started
weight: 10
---

# Getting Started

## Install

Install from PyPi

```
pip3 install cfncli
```

## Walkthrough

This section guides you through a set of `cfn-cli` commands to showcase the functionality of `cfn-cli`. It's assumed you have your CLI setup with valid AWS credentials. If you don't, please setup the AWS CLI and assume a role (preferred) or setup long lived credentials to your account.

This walkthrough will spin up 2 CloudFormation stacks (one in `us-east-1` and another in `us-west-2`) deploying a DynamoDB table in each region, the cost of this table is well within the free tier - hence should not cost anything to deploy for the short duration of the walkthrough.

### Init Config

To initiate a "starter" config, run 

```
cfn-cli generate
```

This will create a `cfn-cli.yaml` configuration file in your current working directory, which we can use for the remainder of this walkthrough. Feel free to open the file in the editor of your choice, we will make changes to the file to showcase producing changesets in a future step.

### Validate Configuration

Run:

```
cfn-cli validate
```

This step verifies the configuration is valid and also confirms any AWS Account configuration checks at the same time (currently not set in the config file)

### Deploy Stacks

Run:

```
cfn-cli stack deploy
```

This will deploy a "dev" and "prod" stack in us-east-1 and us-west-2 respectively. You will see the `cfn-cli` tool deploys one stack after the other (we did not set the option for stack selection, hence by default all stages and all stacks are selected). The events on stack creation are tailed by `cfn-cli` so that you can see the status of resources as they are created.

Output will look like 

```
Deploying stack Develop.DDBTable
StackName: dev-DDBTable
Profile: default
Region: us-east-1
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
StackID: arn:aws:cloudformation:us-east-1:<account_number>:stack/dev-DDBTable/abc6f700-a3a5-11f0-b27b-12bc27b631d7
Created: 2025-10-07 17:47:19.680000+00:00
TerminationProtection: False
Drift Status: NOT_CHECKED
10/07/25 17:47:19 - CREATE_IN_PROGRESS	- dev-DDBTable (AWS::CloudFormation::Stack) - User Initiated
10/07/25 17:47:22 - CREATE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 17:47:23 - CREATE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table) - Resource creation Initiated
10/07/25 17:47:35 - CREATE_COMPLETE	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 17:47:36 - CREATE_COMPLETE	- dev-DDBTable (AWS::CloudFormation::Stack)
Stack deployment complete.
Deploying stack Prod.DDBTable
StackName: prod-DDBTable
Profile: default
Region: us-west-2
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
StackID: arn:aws:cloudformation:us-west-2:<account_number>:stack/prod-DDBTable/bec24760-a3a5-11f0-a20c-0aaee02dfd45
Created: 2025-10-07 17:47:51.901000+00:00
TerminationProtection: False
Drift Status: NOT_CHECKED
10/07/25 17:47:51 - CREATE_IN_PROGRESS	- prod-DDBTable (AWS::CloudFormation::Stack) - User Initiated
10/07/25 17:47:54 - CREATE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 17:47:55 - CREATE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table) - Resource creation Initiated
10/07/25 17:48:06 - CREATE_COMPLETE	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 17:48:07 - CREATE_COMPLETE	- prod-DDBTable (AWS::CloudFormation::Stack)
Stack deployment complete.
```


### Produce ChangeSet

Using the editor of your choice update the `WriteCapacityUnits` for the Production stage, DDBTable stack. This is on line 44. Set this value to a larger number, say 20. Then run:

```
cfn-cli -s prod.* stack changeset create --store
```

This targets all stacks under the "prod" stage (in our case we only have one stack) and will produce a changeset, display it (with pretty printing) and also save the changeset to a default file `.cfn-cli.changesets` (this is what the `--store` flag instructs `cfn-cli` to do).

The output will look like:

```
Generating Changeset for stack prod.DDBTable
StackName: prod-DDBTable
Profile: default
Region: us-west-2
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
ChangeSet Name: prod-DDBTable-3e62f9e0-a3a8-11f0-980a-ded17752aea1
ChangeSet Type: UPDATE
ChangeSet create complete.
ChangeSet Status: CREATE_COMPLETE
Resource Changes:
  myDynamoDBTable (AWS::DynamoDB::Table):
    Action: Modify
    Replacement: False
    Physical Resource: prod-DDBTable-myDynamoDBTable-OXK3I6F8LNR5
    Change Scope: Properties
    Changed Properties:
      ProvisionedThroughput:
        Requires Recreation: Never
        Attribute Change Type: Properties
        Causing Entity: WriteCapacityUnits
        Change Source: ParameterReference
        Value Change: 10 -> 20
ChangeSet creation complete.
```

You can examine the changeset file 

```
cat .cfn-cli.changesets
```

As you can see this contains a JSON file with every stack/stack and the changeset ARN produced (again in our case just the one)

### Execute ChangeSet

Run: 

```
cfn-cli stack changeset exec -i
```

This command attempts to run all changesets across all stacks. The `-i` flag tells `cfn-cli` to ignore that fact that changesets may not exist for all stacks and move onto the next stack - Hence why the error message "ChangeSet for dev.DDBTable does not exist, skipping...." would have been displayed.

Output will look like: 

```
ChangeSet for dev.DDBTable does not exist, skipping....
Executing Changeset prod-DDBTable-3e62f9e0-a3a8-11f0-980a-ded17752aea1 on stack prod.DDBTable
Profile: default
Region: us-west-2
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
Disabling TerminationProtection
10/07/25 18:08:55 - UPDATE_IN_PROGRESS	- prod-DDBTable (AWS::CloudFormation::Stack) - User Initiated
10/07/25 18:08:58 - UPDATE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 18:09:13 - UPDATE_COMPLETE	- myDynamoDBTable (AWS::DynamoDB::Table)
10/07/25 18:09:14 - UPDATE_COMPLETE_CLEANUP_IN_PROGRESS	- prod-DDBTable (AWS::CloudFormation::Stack)
10/07/25 18:09:15 - UPDATE_COMPLETE	- prod-DDBTable (AWS::CloudFormation::Stack)
ChangeSet execution complete.
```

We could have instead targeted the same production stage as we did with the creation of changesets i.e. `cfn-cli -s prod.* changeset exec` 

### Delete Stacks

To delete both stacks, run:

```
cfn-cli stack delete
```

You will notice that they delete in opposite order of creation, in this case prod first then dev. You will be prompted to confirm the deletion of multiple stacks, to avoid this prompt you can use the `-q` flag i.e. `cfn-cli stack delete -q`

Output will look like:

```
Deleting stack prod.DDBTable
StackName: prod-DDBTable
Profile: default
Region: us-west-2
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
Disabling TerminationProtection
StackID: arn:aws:cloudformation:us-west-2:<account_number>:stack/prod-DDBTable/bec24760-a3a5-11f0-a20c-0aaee02dfd45
Created: 2025-10-07 17:47:51.901000+00:00
Last Updated: 2025-10-07 18:08:55.574000+00:00
TerminationProtection: False
Drift Status: NOT_CHECKED
10/07/25 18:12:18 - DELETE_IN_PROGRESS	- prod-DDBTable (AWS::CloudFormation::Stack) - User Initiated
10/07/25 18:12:20 - DELETE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table)
Stack delete complete.
Deleting stack dev.DDBTable
StackName: dev-DDBTable
Profile: default
Region: us-east-1
Account: <account_number>
Identity: arn:aws:sts::<account_number>:assumed-role/Admin/assumed-role
Disabling TerminationProtection
StackID: arn:aws:cloudformation:us-east-1:<account_number>:stack/dev-DDBTable/abc6f700-a3a5-11f0-b27b-12bc27b631d7
Created: 2025-10-07 17:47:19.680000+00:00
TerminationProtection: False
Drift Status: NOT_CHECKED
10/07/25 18:12:50 - DELETE_IN_PROGRESS	- dev-DDBTable (AWS::CloudFormation::Stack) - User Initiated
10/07/25 18:12:52 - DELETE_IN_PROGRESS	- myDynamoDBTable (AWS::DynamoDB::Table)
Stack delete complete.
```