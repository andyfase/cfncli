# AWS CloudFormation CLI

<div style="display: flex; align-items: center; gap: 10px;">

<a href="https://htmlpreview.github.io/?https://github.com/andyfase/cfncli/blob/python-coverage-comment-action-data/htmlcov/index.html">
<img height="24" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andyfase/cfncli/python-coverage-comment-action-data/endpoint.json&label=Code%20Coverage" alt="Coverage badge">
</a>

<a href="https://cfncli.readthedocs.io/" title="CFN CLI Documentation">
<img height="24" src="https://img.shields.io/badge/Docs-Read%20The%20Docs-blue" alt="Documentation">
</a>

</div>
<br/>

The missing CloudFormation CLI. Reborn!

`cfn-cli` is the CloudFormation CLI that AWS never built. Its use dramatically increases the developer friendliness of using CloudFormation at scale, both within developer environments and CI/CD pipelines.

It's designed to be as light a wrapper around CloudFormation as possible, thus avoiding any kind of lock-in. Its use simplifies stack configuration and deployment while allowing for an easy exit to raw CloudFormation JSON style configuration files if desired.

Features:

* Simple and Intuitive CLI that encapsulates the complexity of CloudFormation operations (Packaging, ChangeSets, Drift, Status etc)
* Useful and colourful stack deployment output with full event tailing
* DRY Configuration of stacks in a single YAML file
* Supports ordered stack operations across AWS accounts and regions
* Automatic packaging of external resources (Lambda Code, Nested Stacks and many more resources)
* Loosely coupled cross-stack parameter reference that work cross-region and cross-account
* Nested ChangeSet support, including full and friendly pretty printing.
* Stack configuration inheritance across stages and blueprints

`cfn-cli` in action:

![demo](docs/docs/assets/demo.gif)

## Compatibility

This tool supports Python 3.10 and above. `cfn-cli` has been tested and validated operational on AWS CloudShell, AWS Cloud 9, AWS Linux 2023 AMIs and within CI/CD pipeline runners operating in GitHub, Gitlab and Azure DevOps.

## License

This tool is distributed under the MIT license. The AWS CLI dependent code is distributed under the Apache 2.0 license - see ext_customizations [README](./cfncli/ext_customizations/README.md) and [LICENCE](./cfncli/ext_customizations/LICENSE.md).


## Install

> [!IMPORTANT] 
> Python 3.10 and above is required to install `cfn-cli`

Install from PyPi

```
pip3 install cfncli
```

## Documentation

See [https://cfncli.readthedocs.io/](https://cfncli.readthedocs.io/) for documentation covering usage of the CLI and its configuration syntax  

## Development

See [DEVELOPMENT.md](./DEVELOPMENT.md) for build instructions and development workflow.

## `cfn-cli` Origin Acknowledgement

This code base was forked from [https://github.com/Kotaimen/awscfncli](https://github.com/Kotaimen/awscfncli) who should be acknowledged as the original creator of `cfn-cli`. The original repo became unsupported and dependencies between it and the native AWS CLI caused install issues and compatibility issues.

I have forked and detached this repo from the original codebase and have spent significant effort in updating dependencies, bringing in modern unit tests, fixing bugs, adding documentation and continue to add new features.

This code base will continue to be maintained separately with feature development that will likely not be paralleled in the original code base. 



