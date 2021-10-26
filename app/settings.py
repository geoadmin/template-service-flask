import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ENV_FILE = os.environ.get('ENV_FILE')

if ENV_FILE is not None:
    logger.debug("Loading env file %s", ENV_FILE)
    load_dotenv(dotenv_path=ENV_FILE)
else:
    logger.debug("No env file set, loading settings only from env variables")

BASE_DIR = Path(__file__).parent.parent.resolve(strict=True)

HTTP_PORT = str(os.getenv('HTTP_PORT', "5000"))
LOGS_DIR = os.getenv('LOGS_DIR', str(BASE_DIR / 'logs'))
os.environ['LOGS_DIR'] = LOGS_DIR  # Set default if not set
LOGGING_CFG = os.getenv('LOGGING_CFG', 'logging-cfg-local.yml')
TRAP_HTTP_EXCEPTIONS = True

# Definition of the allowed domains for CORS implementation
ALLOWED_DOMAINS_STRING = os.getenv('ALLOWED_DOMAINS')
if ALLOWED_DOMAINS_STRING is None or ALLOWED_DOMAINS_STRING == "":
    logger.error("No allowed pattern from env was found")
    raise RuntimeError("Environment variable $ALLOWED_DOMAINS was not set")

ALLOWED_DOMAINS = ALLOWED_DOMAINS_STRING.split(',')
