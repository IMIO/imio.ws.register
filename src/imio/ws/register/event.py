# -*- coding: utf-8 -*-

import logging
import os
import requests


logger = logging.getLogger("imio.ws.register")


def zope_started(event):
    keys = {
        "CLIENT_ID": "client_id",
        "APPLICATION_ID": "application_id",
        "APPLICATION_URL": "url",
    }
    values = {v: os.getenv(k) for k, v in keys.items() if os.getenv(k)}
    ws_url = os.getenv("WS_URL")
    if ws_url and len(values.keys()) == 3:
        result = register(ws_url, values)
        logger.info(result)
    else:
        logger.info("missing parameters for route registration")


def register(url, parameters):
    router_url = "{0}/router".format(url)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    error_msg = u"An error occured during route registration: {0}"

    try:
        url = "{ws_url}/route/{client_id}/{application_id}".format(
            ws_url=url,
            **parameters
        )
        result = requests.get(url, headers=headers)
    except Exception as e:
        return error_msg.format(e.message)
    if result.status_code != 200:
        return error_msg.format(result.json().get("errors"))
    result_body = result.json()
    if result_body == parameters:
        return u"Route already exist and up to date"
    if "client_id" not in result_body:
        me = requests.post  # new route
    else:
        me = requests.patch  # existing route with new values

    try:
        result = me(router_url, headers=headers, json=parameters)
    except Exception as e:
        return error_msg.format(e.message)
    if result.status_code != 200:
        return error_msg.format(result.json().get("errors"))
    return result.json()["msg"]
