import logging
import os
import re
import time

from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import abort
from flask import g
from flask import request

from app import settings
from app.helpers.utils import ALLOWED_DOMAINS_PATTERN
from app.helpers.utils import make_error_msg

logger = logging.getLogger(__name__)
route_logger = logging.getLogger('app.routes')

# Standard Flask application initialisation

app = Flask(__name__)
app.config.from_object(settings)


def is_domain_allowed(domain):
    return re.match(ALLOWED_DOMAINS_PATTERN, domain) is not None


# NOTE it is better to have this method registered first (before validate_origin) otherwise
# the route might not be logged if another method reject the request.
@app.before_request
def log_route():
    g.setdefault('request_started', time.time())
    route_logger.info('%s %s', request.method, request.path)


# Reject request from non allowed origins
@app.before_request
def validate_origin():
    # The Origin header is automatically set by the browser and cannot be changed by the javascript
    # application. Unfortunately this header is only set if the request comes from another origin.
    # Sec-Fetch-Site header is set to `same-origin` by most of the browsers except by Safari!
    # The best protection would be to use the Sec-Fetch-Site and Origin header, however this is
    # not supported by Safari. Therefore we added a fallback to the Referer header for Safari.
    sec_fetch_site = request.headers.get('Sec-Fetch-Site', None)
    origin = request.headers.get('Origin', None)
    referrer = request.headers.get('Referer', None)

    if origin is not None:
        if is_domain_allowed(origin):
            return
        logger.error('Origin=%s does not match %s', origin, ALLOWED_DOMAINS_PATTERN)
        abort(403, 'Permission denied')

    if sec_fetch_site is not None:
        if sec_fetch_site in ['same-origin', 'same-site']:
            return
        logger.error('Sec-Fetch-Site=%s is not allowed', sec_fetch_site)
        abort(403, 'Permission denied')

    if referrer is not None:
        if is_domain_allowed(referrer):
            return
        logger.error('Referer=%s does not match %s', referrer, ALLOWED_DOMAINS_PATTERN)
        abort(403, 'Permission denied')

    logger.error('Referer and/or Origin and/or Sec-Fetch-Site headers not set')
    abort(403, 'Permission denied')


# Add CORS Headers to all request
@app.after_request
def add_cors_header(response):
    if (
        'Origin' in request.headers and
        re.match(ALLOWED_DOMAINS_PATTERN, request.headers['Origin'])
    ):
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


# NOTE it is better to have this method registered last (after add_cors_header) otherwise
# the response might not be correct (e.g. headers added in another after_request hook).
@app.after_request
def log_response(response):
    route_logger.info(
        "%s %s - %s",
        request.method,
        request.path,
        response.status,
        extra={
            'response': {
                "status_code": response.status_code, "headers": dict(response.headers.items())
            },
            "duration": time.time() - g.get('request_started', time.time())
        }
    )
    return response


# Register error handler to make sure that every error returns a json answer
@app.errorhandler(Exception)
def handle_exception(err):
    """Return JSON instead of HTML for HTTP errors."""
    if isinstance(err, HTTPException):
        logger.error(err)
        return make_error_msg(err.code, err.description)

    logger.exception('Unexpected exception: %s', err)
    return make_error_msg(500, "Internal server error, please consult logs")


from app import routes  # isort:skip pylint: disable=wrong-import-position
