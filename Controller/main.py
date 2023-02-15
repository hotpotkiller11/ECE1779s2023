
from flask import  request, g
import datetime
from Controller import webapp, controller
import random
import mysql.connector
from Controller.config import db_config
from apscheduler.schedulers.background import BackgroundScheduler
from Controller.CacheController import CacheController
import atexit
import json
import requests


@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    node = controller.get_node(key)
    requests.post(node + "/put", json = json.dumps(request.json))
    

@webapp.route('/get', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    node = controller.get_node(key)
    requests.post(node + "/get", json = json.dumps(request.json))

@webapp.route('/clear',methods=['POST', 'GET'])
def CLEAR():
    # clear all activated nodes
    nodes = controller.activated_nodes()
    for node in nodes:
        requests.post(node + "/clear")
