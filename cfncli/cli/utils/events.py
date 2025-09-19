# -*- encoding: utf-8 -*-

import time
import threading
import click
import botocore.exceptions
from cfncli.runner.commands.utils import is_stack_does_not_exist_exception

from .colormaps import STACK_STATUS_TO_COLOR

print_mutex = threading.Lock()

MAX_PRINT_RESOURCE_ID = 40


class StoppableTailThread:
    def __init__(self, thread, stop_event):
        self.thread = thread
        self.stop_event = stop_event

    def stop(self):
        self.stop_event.set()


def start_tail_stack_events_daemon(
    session,
    stack,
    latest_events=1,
    event_limit=10000,
    time_limit=3600,
    check_interval=5,
    indent=0,
    prefix=None,
    stop_event=None,
    show_physical_resources=False,
):
    """Start tailing stack events"""

    # TODO: Now this causes AWS throttling boto3 call if the tracking stack
    #       contains a lot of nested stacks and/or long update history.
    #       Should implement a barrier on how many querys are being sent
    #       concurrently.

    if stop_event is None:
        stop_event = threading.Event()
    thread = threading.Thread(
        target=tail_stack_events,
        args=(
            session,
            stack,
            latest_events,
            event_limit,
            time_limit,
            check_interval,
            indent,
            prefix,
            stop_event,
            show_physical_resources,
        ),
    )
    thread.daemon = True
    thread.start()
    return StoppableTailThread(thread, stop_event)


def tail_stack_events(
    session,
    stack,
    latest_events=1,
    event_limit=10000,
    time_limit=3600,
    check_interval=5,
    indent=0,
    prefix="XX",
    stop_event=None,
    show_physical_resources=False,
):
    """Tail stack events and print them"""
    then = time.time()

    visited_events = set()

    visited_stacks = set()
    visited_stacks.add(stack.stack_id)

    first_run = True

    # loop until time limit or stop event
    while time.time() - then < time_limit:
        # check if we should stop
        if stop_event and stop_event.is_set():
            break
        # or too many events are visited
        if len(visited_events) > event_limit:
            break

        # get all stack events
        try:
            events = list(stack.events.all())
        except (botocore.exceptions.ClientError, botocore.exceptions.ValidationError) as e:
            if not is_stack_does_not_exist_exception(e):
                click.echo(str(e))
            break
        else:
            # put latest events at first
            events.reverse()
            event_count = len(events)

        # https://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html#event
        for n, e in enumerate(events):
            # skip visited events
            if e.event_id in visited_events:
                continue
            else:
                visited_events.add(e.event_id)

            # tail only latest events
            if first_run:
                if latest_events > 0:
                    if n < event_count - latest_events:
                        continue

            # tail sub stack events
            if (
                e.resource_type == "AWS::CloudFormation::Stack"
                and e.physical_resource_id
                and e.physical_resource_id not in visited_stacks
            ):
                visited_stacks.add(e.physical_resource_id)

                cfn = session.resource("cloudformation", region_name=stack.meta.client.meta.region_name)
                sub_stack = cfn.Stack(e.physical_resource_id)

                # Share the same stop_event so nested threads stop with parent
                start_tail_stack_events_daemon(
                    session,
                    sub_stack,
                    latest_events=latest_events,
                    check_interval=check_interval + 1,
                    indent=indent + 2,
                    prefix=e.logical_resource_id,
                    stop_event=stop_event,
                    show_physical_resources=show_physical_resources,
                )

            # print the event - as we have multiple prints on same line we use a mutex to ensure we dont
            # print half before another thread (used for another sub-stack) starts printing
            with print_mutex:
                if indent > 0:
                    click.echo(" " * indent, nl=False)
                    click.secho("[%s] " % prefix, bold=True, nl=False)

                click.echo(e.timestamp.strftime("%x %X"), nl=False)
                click.echo(" - ", nl=False)
                click.secho(e.resource_status, nl=False, **STACK_STATUS_TO_COLOR[e.resource_status])
                click.echo("\t- %s (%s)" % (e.logical_resource_id, e.resource_type), nl=False)

                if e.resource_status_reason:
                    click.echo(" - %s" % e.resource_status_reason)
                elif e.physical_resource_id and (
                    show_physical_resources or len(e.physical_resource_id) < MAX_PRINT_RESOURCE_ID
                ):
                    click.echo(" - %s" % e.physical_resource_id)
                else:
                    click.echo("")

        else:
            first_run = False

        time.sleep(check_interval)
