from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
import datetime
from BackEnd import webapp
import sys
import random
import mysql.connector
from BackEnd.config import db_config
# from BackEnd.module import somemethod
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

def subfunction1(key):
    """do something with key"""
    print(key)


def subfunction2():
    """do something"""
    print("method2")


"""Front End BackEnd End link"""
@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    #   base page unused test only
    return "welcome 2023"

@webapp.route('/function1', methods=['POST', 'GET'])
def Function1():
    key = request.json["key"]
    return subfunction1(key)

@webapp.route('/function2', methods=['POST', 'GET'])
def Fuction2():
    return subfunction2()

