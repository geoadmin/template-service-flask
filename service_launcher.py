'''Service launcher to use Flask without wsgi.py
'''
from app.helpers.utils import init_logging

# Initialize Logging using JSON format for all loggers and using the Stream Handler.
init_logging()

# pylint: disable=unused-import,wrong-import-position
from app import app  # pylint: disable=unused-import