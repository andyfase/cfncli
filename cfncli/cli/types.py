"""Custom Click parameter types with completion."""

import click
from cfncli.cli.autocomplete import stack_auto_complete, profile_auto_complete


class StackType(click.ParamType):
    """Custom type for stack parameter with completion."""

    name = "stack"

    def shell_complete(self, ctx, param, incomplete):
        """Provide shell completion for stack names."""
        return stack_auto_complete(ctx, param, incomplete)


class ProfileType(click.ParamType):
    """Custom type for profile parameter with completion."""

    name = "profile"

    def shell_complete(self, ctx, param, incomplete):
        """Provide shell completion for AWS profiles."""
        return profile_auto_complete(ctx, param, incomplete)
