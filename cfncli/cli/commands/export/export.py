import os

import click

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.config import ANNOTATED_SAMPLE_CONFIG, DEFAULT_CONFIG_FILE_NAMES
from cfncli.runner.commands.stack_export_command import StackExportOptions, StackExportCommand


@click.command("export")
@click.option(
    "--output-dir",
    default="cfn-cli-export",
    help="output export directory to save CloudFormation JSON files for stacks",
)
@click.pass_context
@command_exception_handler
def cli(ctx, output_dir):
    """Exports cfn-cli stack configuration.

    Exports cfn-cli stack configuration to native AWS CloudFormation CLI JSON files (Parameters, Tags JSON files).
    """
    assert isinstance(ctx.obj, Context)

    options = StackExportOptions(
        output_dir=output_dir,
    )

    command = StackExportCommand(pretty_printer=ctx.obj.ppt, options=options)
    _ = ctx.obj.runner.run(command)
