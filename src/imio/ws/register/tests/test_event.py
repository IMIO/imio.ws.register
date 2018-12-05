# -*- coding: utf-8 -*-

from imio.ws.register import event
from mock import Mock
from requests.exceptions import ConnectionError

import mock
import os
import requests
import unittest


class TestEvent(unittest.TestCase):
    """Test event that register the application to the webservice"""
    _env_keys = (
        'CLIENT_ID',
        'APPLICATION_ID',
        'APPLICATION_URL',
        'WS_URL',
    )

    def _set_environ(self):
        os.environ['CLIENT_ID'] = 'FOO'
        os.environ['APPLICATION_ID'] = 'BAR'
        os.environ['APPLICATION_URL'] = 'http://app.com'
        os.environ['WS_URL'] = 'http://ws.com'

    def setUp(self):
        self._requests_post = requests.post
        self._register = event.register

    def tearDown(self):
        for k in self._env_keys:
            if k in os.environ:
                del os.environ[k]

        requests.post = self._requests_post
        event.register = self._register

    @mock.patch('imio.ws.register.event.logger')
    def test_event_zope_started_success(self, mock_logger):
        event.register = Mock(return_value='message')
        self._set_environ()
        event.zope_started(None)
        mock_logger.info.assert_called_with('message')

    @mock.patch('imio.ws.register.event.logger')
    def test_event_zope_started_missing_parameters(self, mock_logger):
        """Test when some parameters are missings"""
        event.register = Mock(return_value='message')
        excepted_message = 'missing parameters for route registration'
        for key in self._env_keys:
            self._set_environ()
            del os.environ[key]
            event.zope_started(None)
            mock_logger.info.assert_called_with(excepted_message)

    def test_register_request_exception(self):
        """Test when an error is raised by requests"""
        requests.post = Mock(side_effect=ConnectionError('error 1'))
        msg = event.register('http://localhost', {})
        self.assertEqual(
            u'An error occured during route registration: error 1',
            msg,
        )

    def test_register_wrong_status(self):
        """Test when the response status code is not 200"""
        response = type('response', (object, ), {
            'status_code': 400,
            'json': lambda x: {'errors': 'error 2'},
        })
        requests.post = Mock(return_value=response())
        msg = event.register('http://localhost', {})
        self.assertEqual(
            u'An error occured during route registration: error 2',
            msg,
        )

    def test_register_200(self):
        """Test when the response status code is 200"""
        response = type('response', (object, ), {
            'status_code': 200,
            'json': lambda x: {'msg': 'success'},
        })
        requests.post = Mock(return_value=response())
        msg = event.register('http://localhost', {})
        self.assertEqual(u'success', msg)
