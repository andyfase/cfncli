import logging


def handler(event, context):
    logger = logging.getLogger(__name__)
    logger.info("hello world")
    return {"success": True}
