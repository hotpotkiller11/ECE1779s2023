from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
import datetime
from BackEnd import webapp
import sys
import random
import mysql.connector
from BackEnd.config import db_config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json

"""Global variables"""
global memcacheConfig


"""DB config """
def init_db():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = init_db()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    """Safe tear down"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

"""
example of sql query in python
def get_configinfo():
    cnx = get_db()
    query = '''SELECT capacity, policy
                    FROM configurations WHERE config_id = 1;''' # some query
    cursor = cnx.cursor()
    cursor.execute(query)
    rows = cursor.fetchall() # some info
    cnx.close()
    memcacheConfig = {'capacity': rows[0][0], 'policy': rows[0][1]} # some info

    return memcacheConfig
"""

"""Funcitions"""

def subPut(key,value):
    """do something with key"""
    print(key,value)
    response = webapp.response_class(
        response=json.dumps(key+value),
        status=200,
        mimetype='application/json',
    )
    return response


def subGET(key):
    """do something"""
    print("method2")
    response = webapp.response_class(
        response=json.dumps(key),
        status=200,
        mimetype='application/json',
    )
    return response

def subCLEAR():
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response

def InvalidateKey(key):
    response = webapp.response_class(
        response=json.dumps("ok"),
        status=200,
        mimetype='application/json',
    )
    return response

def refreshConfiguration():
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response




"""Front End BackEnd End link"""
@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    #   base page unused test only
    return "welcome 2023"

@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    value = request.json["value"]
    return subPut(key,value)

@webapp.route('/get', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    #return subGET(key)
    return subGET(key)

@webapp.route('/clear',methods=['POST', 'GET'])
def CLEAR():
    return subCLEAR()




