import logging
import unittest

from nose2.tools import params

from flask import url_for

from app import app
from app.version import APP_VERSION

logger = logging.getLogger(__name__)


class CheckerTests(unittest.TestCase):

    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()
        self.app = app.test_client()
        self.app.testing = True
        self.origin_headers = {"allowed": {"Origin": "some_random_domain"}}

    def test_checker(self):
        response = self.app.get(url_for('checker'), headers=self.origin_headers["allowed"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})

    def test_checker_non_allowed_origin(self):
        response = self.app.get(url_for('checker'), headers=self.origin_headers["bad"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["error"]["message"], "Not allowed")

    @params(
        None,
        {'Origin': 'www.example'},
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'cross-site'
        },
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'same-site'
        },
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'same-origin'
        },
        {'Referer': 'http://www.example'},
    )
    def test_feedback_non_allowed_origin(self, headers):
        response = self.app.get(url_for('checker'), headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["error"]["message"], "Not allowed")


    @params(
        {'Origin': 'map.geo.admin.ch'},
        {
            'Origin': 'map.geo.admin.ch', 'Sec-Fetch-Site': 'same-site'
        },
        {
            'Origin': 'public.geo.admin.ch', 'Sec-Fetch-Site': 'same-origin'
        },
        {
            'Origin': 'http://localhost', 'Sec-Fetch-Site': 'cross-site'
        },
        {'Sec-Fetch-Site': 'same-origin'},
        {'Referer': 'https://map.geo.admin.ch'},
    )
    def test_feedback_allowed_origin(self, headers):
        response = self.app.get(url_for('checker'), headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertCors(response, check_origin=False)
