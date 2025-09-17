"""Dynamic Autocomplete helpers"""

import click
from click.shell_completion import CompletionItem

from cfncli.config import find_default_config, load_config, ConfigError


def profile_auto_complete(ctx, param, incomplete):
    """Autocomplete for --profile

    Lists any profile name contains given incomplete.
    """
    import boto3

    profiles = boto3.session.Session().available_profiles
    return [CompletionItem(p) for p in profiles if incomplete in p]


def stack_auto_complete(ctx, param, incomplete):
    """Autocomplete for --stack

    By default, returns qualified names start with qualified stack
    """
    # Get config file from context params
    config_filename = ctx.params.get("file") if ctx.params else "./cfn-cli.yaml"
    config_filename = find_default_config(config_filename)
    try:
        deployments = load_config(config_filename)
    except (ConfigError, Exception) as ex:
        # ignore any config parsing errors
        return []

    # remove meta chars
    incomplete_clean = incomplete.lower().translate({"*": "", "?": ""})

    return [
        CompletionItem(s.stack_key.qualified_name)
        for s in deployments.query_stacks()
        if s.stack_key.qualified_name.lower().startswith(incomplete_clean)
    ]
