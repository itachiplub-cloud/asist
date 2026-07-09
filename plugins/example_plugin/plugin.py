from utils.logger import logger


def setup():
    logger.info("Example plugin loaded")
    # Register handlers or initialize resources here


def teardown():
    logger.info("Example plugin unloaded")
    # Cleanup resources here
