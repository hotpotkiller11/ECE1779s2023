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
global Config
filesize = 0 # Size of the current figures in cache memory (unit: byte)

"""mem cache structure"""
mem_dict = {}
key_queue = [] # LRU list, from the most recent use to the least recent use

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


def get_config_info():
    cnx = get_db()
    query = '''SELECT capacity, policy
                    FROM backend_config where id = (
        select max(id) FROM backend_config);'''
    cursor = cnx.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    # cnx.close() This might cause failure
    global Config
    Config = {'capacity': rows[0][0], 'policy': rows[0][1]}


def RandomReplacement(size: int) -> None: #random
    global filesize
    capacity = Config['capacity']
    while filesize + size > capacity:
        remove_index = random.randint(0, len(key_queue) - 1)
        removed_key = key_queue.pop(remove_index)
        removed_file = mem_dict.pop(removed_key)
        filesize -= len(removed_file)


def LeastRecentlyUsed(size: int) -> None: #LRU
    global filesize
    capacity = Config['capacity']
    while filesize + size > capacity:
        removed_key = key_queue.pop() # The last one in the LRU list will be removed
        removed_file = mem_dict.pop(removed_key)
        filesize -= len(removed_file)


def mem_cleanup(size: int) -> bool:
    '''
        Try to clean up a space for a incoming file.
        Return if the cleanup is successful
    '''
    capacity = Config['capacity']
    policy = Config['policy']
    if filesize + size <= capacity: return False
    if policy == "random":
        print("random")
        RandomReplacement(size)
    else:
        print("lru")
        LeastRecentlyUsed(size)
    return True


def mem_add(key: str, file: bytes) -> bool:
    '''
        Try to add a file into the mem cache system. The function will try to delete
        old files to store the new file (replacement included).

        Return if the file add to memory successfully.
        Return false if the new file exceeds the mem capacity or exceptions in storing
    '''
    global filesize
    if key in mem_dict: return False
    capacity = Config['capacity']
    print(capacity)
    size = len(file)
    if size > capacity: return False
    if size + filesize > capacity:
        mem_cleanup(size)
    mem_dict[key] = file
    key_queue.insert(0, key)
    filesize += size
    return True


def mem_clear() -> None:
    '''
    Clear the mem cache.
    '''
    global filesize
    global mem_dict
    global key_queue
    mem_dict = {}
    key_queue = []
    filesize = 0


def mem_get(key: str): #-> bytes | None:
    '''
        Get the file stored in memory.
        Return None if key not in the dictionary.
    '''
    if key not in mem_dict: return None
    key_queue.remove(key)
    key_queue.insert(0, key) # Place the key to the most recent used
    return mem_dict[key]

def mem_invalidate(key: str) -> bool:
    '''
        Try to invalidate a key from mem cache
        Return true if the key was found and removed
        Return false if key not found in mem cache
    '''
    global filesize
    if key not in mem_dict: return False
    key_queue.remove(key)
    removed = mem_dict.pop(key)
    filesize -= len(removed) # decrease size
    return True

"""Funcitions"""

def invalidateKey(key):
    result = mem_invalidate(key)
    if result == False:
        print("No such key") # still ok
    response = webapp.response_class(
        response=json.dumps("ok"),
        status=200,
        mimetype='application/json',
    )
    return response

def refreshConfiguration():
    get_config_info()   #configuration refresh, read in refresh
    response = webapp.response_class(
        response=json.dumps(Config),
        status=200,
        mimetype='application/json',
    )
    return response

def subPUT(key,value):
    """put the key in to the cache"""
    print("call put")
    mem_add(key, value)
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response


def subGET(key):
    """do something"""
    print("get")
    if key in key_queue:
        img = mem_dict[key]
        data = {
            "success": "true",
            "key": key,
            "content": img
        }
        response = webapp.response_class(
            response=json.dumps(data),# why not img
            status=200,
            mimetype='application/json',
        )
    else:
        response = webapp.response_class(
            response=json.dumps("MISS"),
            status=404,
            mimetype='application/json',
        )
    return response

def subCLEAR():
    mem_clear()
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    #   base page unused test only
    return "Test page--welcome to back end"

@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    value = request.json["value"]
    return subPUT(key,value)

@webapp.route('/get', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    #return subGET(key)
    return subGET(key)

@webapp.route('/clear',methods=['POST', 'GET'])
def CLEAR():
    return subCLEAR()

@webapp.route('/invalidatekey',methods=['POST', 'GET'])
def INVALIDATEKEY():
    return invalidateKey()

@webapp.route('/keys',methods=['GET'])
def keys():
    keys = sorted(key_queue) # ascending order
    data = {
            "success": "true",
            "keys": keys,
            "size": filesize
        }
    response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json',
        )
    return response

@webapp.route('/refresh',methods= ['POST' , 'GET'])
def REFRESH():
    return refreshConfiguration()

@webapp.route('/testread',methods=['POST', 'GET'])
def TEST():
    print(Config['policy'],Config['capacity'])
    return refreshConfiguration()
