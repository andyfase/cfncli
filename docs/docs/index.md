# Intro

The missing CloudFormation CLI. Reborn!

`cfn-cli` is the CloudFormation CLI that AWS never built. Its use dramatically increases the developer friendliness of using CloudFormation at scale, both within developer environments and CI/CD pipelines.

It's designed to be as light a wrapper around CloudFormation as possible, thus avoiding any kind of lock-in. Its use simplifies stack configuration and deployment while allowing for an easy exit to raw CloudFormation JSON style configuration files if desired.

Features:

- Simple and Intuitive CLI that encapsulates the complexity of CloudFormation operations (Packaging, ChangeSets, Drift, Status  etc) 
- Useful and colourful stack deployment output with full event tailing
- DRY Configuration of stacks in a single YAML file 
- Supports ordered stack operations across AWS accounts and regions
- Automatic packaging of external resources (Lambda Code, Nested Stacks and many more resources)
- Loosely coupled cross-stack parameter reference that work cross-region and cross-account
- Nested ChangeSet support, including full and friendly pretty printing.
- Stack configuration inheritance across stages and blueprints

Example Usage:

![demo](assets/demo.gif)

