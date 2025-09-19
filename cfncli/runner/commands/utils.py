import botocore.exceptions
import backoff
from cfncli.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception


def get_changeset_name(changeset_arn, shorten=True):
    # arn format for changeset arn:aws:cloudformation:region:account-id:changeSet/change-set-name/change-set-id
    return changeset_arn if not shorten else changeset_arn.split("/")[1]


def update_termination_protection(session, termination_protection, stack_name, ppt):
    """Update termination protection on a stack"""

    if termination_protection is None:
        # don't care, don't change
        return

    client = session.client("cloudformation")

    if termination_protection:
        ppt.secho("Enabling TerminationProtection")
    else:
        ppt.secho("Disabling TerminationProtection", fg="red")

    client.update_termination_protection(StackName=stack_name, EnableTerminationProtection=termination_protection)


def is_stack_does_not_exist_exception(ex):
    """Check whether given exception is "stack does not exist",
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError) or isinstance(ex, botocore.exceptions.ValidationError):
        error = ex.response.get("Error", {})
        error_message = error.get("Message", "Unknown")
        return error_message.endswith("does not exist")
    else:
        return False


def is_changeset_does_not_exist_exception(ex):
    """Check whether given exception is "stack does not exist",
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get("Error", {})
        error_message = error.get("Message", "Unknown")
        return error_message.endswith("does not exist")
    else:
        return False


def is_changeset_no_changes(ex):
    """Check whether given exception is "stack does not exist",
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get("Error", {})
        error_message = error.get("Message", "Unknown")
        return "No updates are to be performed" in error_message
    else:
        return False


def is_no_updates_being_performed_exception(ex):
    """Check whether given exception is "no update to be performed"
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get("Error", {})
        error_message = error.get("Message", "Unknown")
        return error_message.endswith("No updates are to be performed.")
    else:
        return False


def is_stack_already_exists_exception(ex):
    """Check whether given exception is "stack already exist"
    Exception class is dynamiclly generated in botocore.
    """
    return ex.__class__.__name__ == "AlreadyExistsException"


###
### Helper functions taken from main classes so they can be re-used and all have backoff set
###


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def create_change_set(client, parameters):
    # remove DisableRollback for creation of changeset only
    changeset_parameters = parameters.copy()
    changeset_parameters.pop("DisableRollback", None)
    return client.create_change_set(**changeset_parameters)


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def execute_change_set(client, parameters):
    return client.execute_change_set(**parameters)


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def create_stack(client, parameters):
    return client.create_stack(**parameters)


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def delete_stack(client, parameters):
    return client.delete_stack(**parameters)


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def update_stack(client, parameters):
    return client.update_stack(**parameters)


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def describe_change_set(client, changeset_name=None, stack_name=None, changeset_arn=None):
    if stack_name and changeset_name:
        return client.describe_change_set(
            ChangeSetName=changeset_name, StackName=stack_name, IncludePropertyValues=True
        )
    elif changeset_arn:
        return client.describe_change_set(ChangeSetName=changeset_arn, IncludePropertyValues=True)
    else:
        raise Exception("invalid parameters to describe_change_set")


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10, giveup=is_not_rate_limited_exception)
def check_changeset_type(client, stack_name):
    try:
        # check whether stack is already created.
        status = client.describe_stacks(StackName=stack_name)
        stack_status = status["Stacks"][0]["StackStatus"]
    except botocore.exceptions.ClientError as e:
        if is_stack_does_not_exist_exception(e):
            return "CREATE", True
        raise
    if len(status["Stacks"]) < 1:
        return "CREATE", True  ## Should never get here as exception handles not existant stack
    stack_status = status["Stacks"][0]["StackStatus"]
    if stack_status == "REVIEW_IN_PROGRESS":
        return "CREATE", True
    return "UPDATE", False
