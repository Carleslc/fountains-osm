"""
App configurations
"""

import logging

APP_NAME = "fountains-osm"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(APP_NAME)


def load_config():
    """
    Load app configuration (logging, environment variables, etc)
    """
    
