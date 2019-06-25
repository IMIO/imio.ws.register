# -*- coding: utf-8 -*-

from imio.ws.register import event
from mock import Mock
from requests.exceptions import ConnectionError

import copy
import mock
import os
import requests
import unittest


class FakeRequestResponse(object):
    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class TestEvent(unittest.TestCase):
    """Test event that register the application to the webservice"""

    _env_keys = ("CLIENT_ID", "APPLICATION_ID", "APPLICATION_URL", "WS_URL")

    def _set_environ(self):
        os.environ["CLIENT_ID"] = "FOO"
        os.environ["APPLICATION_ID"] = "BAR"
        os.environ["APPLICATION_URL"] = "http://app.com"
        os.environ["WS_URL"] = "http://ws.com"

    def setUp(self):
        self._requests_post = requests.post
        self._register = event.register

    def tearDown(self):
        for k in self._env_keys:
            if k in os.environ:
                del os.environ[k]

        requests.post = self._requests_post
        event.register = self._register

    @mock.patch("imio.ws.register.event.logger")
    def test_event_zope_started_success(self, mock_logger):
        event.register = Mock(return_value="message")
        self._set_environ()
        event.zope_started(None)
        mock_logger.info.assert_called_with("message")

    @mock.patch("imio.ws.register.event.logger")
    def test_event_zope_started_missing_parameters(self, mock_logger):
        """Test when some parameters are missings"""
        event.register = Mock(return_value="message")
        excepted_message = "missing parameters for route registration"
        for key in self._env_keys:
            self._set_environ()
            del os.environ[key]
            event.zope_started(None)
            mock_logger.info.assert_called_with(excepted_message)

    @mock.patch(
        "requests.get",
        Mock(
            side_effect=(
                ConnectionError("error 1"),
                FakeRequestResponse(400, {"errors": "error 2"}),
            )
        ),
    )
    def test_register_get_exception(self):
        """Test when an error is raised by requests"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        msg = event.register("http://localhost", parameters)
        self.assertEqual(u"An error occured during route registration: error 1", msg)
        msg = event.register("http://localhost", parameters)
        self.assertEqual(u"An error occured during route registration: error 2", msg)

    def test_register_route_already_exist(self):
        """Test when the route already exist"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        response = FakeRequestResponse(200, parameters)
        with mock.patch("requests.get", Mock(return_value=response)):
            msg = event.register("http://localhost", parameters)
            self.assertEqual(u"Route already exist and up to date", msg)

    @mock.patch("requests.get", Mock(return_value=FakeRequestResponse(200, {})))
    @mock.patch(
        "requests.post",
        Mock(
            side_effect=(
                ConnectionError("error 1"),
                FakeRequestResponse(400, {"errors": "error 2"}),
            )
        ),
    )
    @mock.patch("requests.patch")
    def test_register_post_route_exception(self, patch):
        """Test when the post of the new route fails"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        msg = event.register("http://localhost", parameters)
        self.assertFalse(patch.called)
        self.assertEqual(u"An error occured during route registration: error 1", msg)
        msg = event.register("http://localhost", parameters)
        self.assertFalse(patch.called)
        self.assertEqual(u"An error occured during route registration: error 2", msg)

    @mock.patch(
        "requests.get",
        Mock(
            return_value=FakeRequestResponse(
                200,
                {
                    "client_id": "FOO",
                    "application_id": "BAR",
                    "url": "http://newapp.com",
                },
            )
        ),
    )
    @mock.patch(
        "requests.patch",
        Mock(
            side_effect=(
                ConnectionError("error 1"),
                FakeRequestResponse(400, {"errors": "error 2"}),
            )
        ),
    )
    @mock.patch("requests.post")
    def test_register_patch_route_exception(self, post):
        """Test when the patch of the route fails"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        msg = event.register("http://localhost", parameters)
        self.assertFalse(post.called)
        self.assertEqual(u"An error occured during route registration: error 1", msg)
        msg = event.register("http://localhost", parameters)
        self.assertFalse(post.called)
        self.assertEqual(u"An error occured during route registration: error 2", msg)

    @mock.patch(
        "requests.get",
        Mock(
            return_value=FakeRequestResponse(200, {"msg": "The route does not exist"})
        ),
    )
    @mock.patch(
        "requests.post",
        Mock(return_value=FakeRequestResponse(200, {"msg": "Route added"})),
    )
    def test_register_post(self):
        """Test when a new route is added"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        msg = event.register("http://localhost", parameters)
        self.assertEqual(u"Route added", msg)

    @mock.patch(
        "requests.get",
        Mock(
            return_value=FakeRequestResponse(200, {"msg": "The route does not exist"})
        ),
    )
    @mock.patch(
        "requests.patch",
        Mock(return_value=FakeRequestResponse(200, {"msg": "Route updated"})),
    )
    def test_register_patch(self):
        """Test when a route is updated"""
        parameters = {
            "client_id": "FOO",
            "application_id": "BAR",
            "url": "http://app.com",
        }
        new_parameters = copy.deepcopy(parameters)
        new_parameters["url"] = "http://newapp.com"
        response = FakeRequestResponse(200, parameters)
        with mock.patch("requests.get", Mock(return_value=response)):
            msg = event.register("http://localhost", new_parameters)
            self.assertEqual(u"Route updated", msg)
