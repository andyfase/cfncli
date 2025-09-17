"""Status string to click.style mapping"""

## Color Codes taken frm offical traffic light RGB values
## https://www.cisa.gov/news-events/news/traffic-light-protocol-tlp-definitions-and-usage#:~:text=RGB:,Y=0%2C%20K=100

# TLP:RED : R=255, G=0, B=51, background: R=0, G=0, B=0
# TLP:AMBER : R=255, G=192, B=0, background: R=0, G=0, B=0
# TLP:GREEN : R=51, G=255, B=0, background: R=0, G=0, B=0
rgb_red = dict(fg=[255, 0, 51])
rgb_amber = dict(fg=[255, 192, 0])
rgb_green = dict(fg=[51, 255, 0])

_STACK_STATUS_TO_COLOR = {
    "CREATE_IN_PROGRESS": rgb_amber,
    "CREATE_FAILED": rgb_red,
    "CREATE_COMPLETE": rgb_green,
    "ROLLBACK_IN_PROGRESS": rgb_amber,
    "ROLLBACK_FAILED": rgb_red,
    "ROLLBACK_COMPLETE": rgb_red,
    "DELETE_IN_PROGRESS": rgb_amber,
    "DELETE_FAILED": rgb_red,
    "DELETE_SKIPPED": rgb_red,
    "DELETE_COMPLETE": rgb_green,
    "UPDATE_IN_PROGRESS": rgb_amber,
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS": rgb_green,
    "UPDATE_COMPLETE": rgb_green,
    "UPDATE_ROLLBACK_IN_PROGRESS": rgb_red,
    "UPDATE_ROLLBACK_FAILED": rgb_red,
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS": rgb_red,
    "UPDATE_ROLLBACK_COMPLETE": rgb_green,
    "UPDATE_FAILED": rgb_red,
    "REVIEW_IN_PROGRESS": rgb_amber,
    "IMPORT_FAILED": rgb_red,
    "IMPORT_COMPLETE": rgb_green,
    "IMPORT_IN_PROGRESS": rgb_amber,
    "IMPORT_ROLLBACK_IN_PROGRESS": rgb_red,
    "IMPORT_ROLLBACK_FAILED": rgb_red,
    "IMPORT_ROLLBACK_COMPLETE": rgb_red,
    # custom status:
    "STACK_NOT_FOUND": rgb_red,
}

_CHANGESET_STATUS_TO_COLOR = {
    "UNAVAILABLE": dict(fg="white", dim=True),
    "AVAILABLE": rgb_green,
    "EXECUTE_IN_PROGRESS": rgb_amber,
    "EXECUTE_COMPLETE": rgb_green,
    "EXECUTE_FAILED": rgb_red,
    "OBSOLETE": dict(fg="white", dim=True),
    "CREATE_PENDING": rgb_amber,
    "CREATE_IN_PROGRESS": rgb_amber,
    "CREATE_COMPLETE": rgb_green,
    "DELETE_COMPLETE": rgb_green,
    "FAILED": rgb_red,
}

_CHANGESET_ACTION_TO_COLOR = {
    "Add": rgb_green,
    "Modify": rgb_amber,
    "Remove": rgb_red,
}

_CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR = {
    "Never": rgb_green,
    "Conditionally": rgb_amber,
    "Always": rgb_red,
}

_CHANGESET_REPLACEMENT_TO_COLOR = {
    "True": rgb_red,
    "Conditional": rgb_amber,
    "False": rgb_green,
}

_DRIFT_STATUS_TO_COLOR = {
    "DELETED": rgb_red,
    "MODIFIED": rgb_amber,
    "NOT_CHECKED": dict(fg="white", dim=True),
    "IN_SYNC": rgb_green,
    "UNKNOWN": dict(fg="white", dim=True),
    "DRIFTED": rgb_red,
    "DETECTION_IN_PROGRESS": rgb_amber,
    "DETECTION_FAILED": rgb_red,
    "DETECTION_COMPLETE": rgb_green,
}

_DRIFT_RESOURCE_TYPE_TO_COLOR = {
    "ADD": rgb_green,
    "REMOVE": rgb_red,
    "NOT_EQUAL": rgb_amber,
}


class ColorMap:
    """Return a default colormap when status missing from mapping."""

    def __init__(self, mapping):
        self._mapping = mapping

    def __getitem__(self, status):
        try:
            return self._mapping[status]
        except KeyError:
            return dict()


STACK_STATUS_TO_COLOR = ColorMap(_STACK_STATUS_TO_COLOR)
CHANGESET_STATUS_TO_COLOR = ColorMap(_CHANGESET_STATUS_TO_COLOR)
CHANGESET_ACTION_TO_COLOR = ColorMap(_CHANGESET_ACTION_TO_COLOR)
CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR = ColorMap(_CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR)
CHANGESET_REPLACEMENT_TO_COLOR = ColorMap(_CHANGESET_REPLACEMENT_TO_COLOR)
DRIFT_STATUS_TO_COLOR = ColorMap(_DRIFT_STATUS_TO_COLOR)
DRIFT_RESOURCE_TYPE_TO_COLOR = ColorMap(_DRIFT_RESOURCE_TYPE_TO_COLOR)

## export specific colors for red/amber/green
RED = rgb_red["fg"]
AMBER = rgb_amber["fg"]
GREEN = rgb_green["fg"]
