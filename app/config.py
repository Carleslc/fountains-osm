"""
App configurations
"""

import logging
import logging.config

from uvicorn.config import LOGGING_CONFIG

from os import getenv
from dotenv import load_dotenv

APP_NAME = "fountains-osm"

logger = logging.getLogger(APP_NAME)

def set_logging(level=logging.INFO):
    datetime_format = "%d-%m-%Y %H:%M:%S"

    default_logger = LOGGING_CONFIG["formatters"]["default"]
    default_logger["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
    default_logger["datefmt"] = datetime_format

    access_logger = LOGGING_CONFIG["formatters"]["access"]
    access_logger["fmt"] = '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    access_logger["datefmt"] = datetime_format

    # Configurar el logger de uvicorn
    logging.config.dictConfig(LOGGING_CONFIG)

    # Configurar el logger propio
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s:\t%(message)s",
        datefmt=datetime_format
    )

def load_config():
    """
    Load app configuration (logging, environment variables, etc)
    """

    load_dotenv()

    set_logging(level=logging.getLevelName(getenv('LOG_LEVEL', 'INFO')))
