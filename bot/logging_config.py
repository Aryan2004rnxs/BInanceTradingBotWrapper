import os
import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'trading_bot.log'))

def setup_logging():
    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Keep log size under control (max 5MB, rotating)
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logging()
