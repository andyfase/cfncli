# Feature Development

This lists all features added since the original fork or the code from [https://github.com/Kotaimen/awscfncli](https://github.com/Kotaimen/awscfncli)

##

18/08/2025 - v0.4.0
- Breaking change for changesets - now offering "changeset create" and "changeset execute" options
- Changeset creation can now be optionally saved to disk via `--output` flag
- Changeset executuion via `--input` flag 
- Support ability to extend Stage from another Stage (useful for DR or duplicate deployment regions)

18/08/2025 - v0.3.3
- Add support for nested changeset production and display.
- Fix for nested stack event printing

14/08/2025 - v0.3.2

 - Add `RoleARN` parameter to Stage config to allow any stacks within stage to use the same CloudFormation deployment role.

30/07/2025 - v0.3.X

- Modified Color schema to offical traffic lights colours
- Added ability to see resource values changes in changeset production (requires boto3 / botocore version bump)

29/07/2025 - v0.2.X

- Added distinct `changeset` command to just produce changeset and exit
- Added `DisableRollback` option to stack sync and update (already existed in deploy)

27/11/2023
- Added Stage `Config` section. See Stage `Configuration` in the main [./README.md](README.md)


29/11/2023
- `awscfncli` s3 bucket created with bucket policy that Deny's access unless using SecureTransport.