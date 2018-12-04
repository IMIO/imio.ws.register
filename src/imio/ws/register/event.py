# -*- coding: utf-8 -*-

import logging
import os
import requests


logger = logging.getLogger('imio.ws.register')


def zope_started(event):
    keys = {
        'CLIENT_ID': 'client_id',
        'APPLICATION_ID': 'application_id',
        'APPLICATION_URL': 'url',
    }
    values = {v: os.getenv(k) for k, v in keys.items() if os.getenv(k)}
    ws_url = os.getenv('WS_URL')
    if ws_url and len(values.keys()) == 3:
        result = register(ws_url, values)
        logger.info(result)
    else:
        logger.info('missing parameters for route registration')


def register(url, parameters):
    try:
        result = requests.post(
            '{0}/router'.format(url),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            json=parameters,
        )
    except Exception as e:
        return u'An error occured during route registration: {0}'.format(
            e.message,
        )
    if result.status_code != 200:
        return u'An error occured during route registration: {0}'.format(
            result.json().get('errors'),
        )
    return result.json()['msg']
