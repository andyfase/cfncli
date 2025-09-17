#  -*- encoding: utf-8 -*-

import click

from cfncli.cli.context import Context
from cfncli.cli.utils.deco import command_exception_handler
from cfncli.runner.commands.drift_detect_command import DriftDetectOptions, DriftDetectCommand


@click.command()
@click.option("--no-wait", "-w", is_flag=True, default=False, help="Exit immediately after operation is started.")
@click.option("--no-show-resources", "-nr", is_flag=True, default=False, help="Dont show resources that had drifted.")
@click.pass_context
@command_exception_handler
def detect(ctx, no_wait, no_show_resources):
    """Detect stack drifts."""
    assert isinstance(ctx.obj, Context)

    options = DriftDetectOptions(no_wait=no_wait, no_show_resources=no_show_resources)

    command = DriftDetectCommand(pretty_printer=ctx.obj.ppt, options=options)

    ctx.obj.runner.run(command)
