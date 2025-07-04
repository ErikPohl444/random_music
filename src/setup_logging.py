import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def raise_and_log(logged_exception: Exception, exception_message: str):
    logger.error(exception_message)
    raise logged_exception(exception_message)
