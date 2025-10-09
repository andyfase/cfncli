---
title: CLI Options
weight: 20
---

# Environment Variable Overrides

`FORCE_COLOR`: set this to `true` to force color output. This is needed for CI pipelines which will not pass Clicks "is this a valid tty" test. 

# CLI Options

::: mkdocs-click
    :module: cfncli.cli.main
    :command: cli
    :prog_name: cfn-cli
    :depth: 1
    :style: table
    :list_subcommands: True