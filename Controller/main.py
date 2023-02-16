
from flask import  request, Response
import datetime
from Controller import webapp, control
import random
import mysql.connector
from Controller.config import db_config
from apscheduler.schedulers.background import BackgroundScheduler
from Controller.CacheController import CacheController
import atexit
import json
import requests

def forward_response(res: Response) -> Response:
    """ Get a new response that ready to be returned from another response

    Args:
        res (Response): The response from a request that to be forwarded

    Returns:
        Response: The ne response that ready to be returned
    """
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (k,v) for k,v in res.raw.headers.items()
        if k.lower() not in excluded_headers
    ]
    return Response(res.content, res.status_code, headers)

@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/put", json = request.json)
    return forward_response(res)
    

@webapp.route('/get', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/get", json = request.json)
    return forward_response(res)

@webapp.route('/clear',methods=['POST', 'GET'])
def CLEAR():
    # clear all activated nodes
    nodes = control.activated_nodes()
    for node in nodes:
        requests.post(node + "/clear")
    # no matter what, return a valid feedback
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response
