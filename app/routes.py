import logging

from flask import jsonify
from flask import make_response

from app import app
from app.helpers.route import prefix_route
from app.version import APP_VERSION

logger = logging.getLogger(__name__)

# add route prefix
app.route = prefix_route(app.route, '/v4/template')


@app.route('/checker', methods=['GET'])
def check():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))
