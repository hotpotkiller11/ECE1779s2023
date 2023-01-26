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
                    FROM backend_config;'''
    cursor = cnx.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cnx.close()
    global Config
    Config = {'capacity': rows[0][0], 'policy': rows[0][1]}

def mem_add(key: str, file: bytes) -> bool:
    ''' Try to add a file into the mem cache system. The function will try to delete 
        old files to store the new file (replacement included).

        Return if the file add to memory successfully.
        Return false if the new file exceeds the mem capacity or exceptions in storing
    '''
    global filesize
    if key in mem_dict: return False
    capacity = Config['capacity']
    size = len(file)
    if size > capacity: return False
    if size + filesize > capacity:
        mem_cleanup(size)
    mem_dict[key] = file
    key_queue.insert(0, key)
    filesize += size
    return True

def mem_clear() -> None:
    ''' Clear the mem cache.
    '''
    global filesize
    global mem_dict
    global key_queue
    mem_dict = {}
    key_queue = []
    filesize = 0

def mem_get(key: str) -> bytes | None:
    ''' Get the file stored in memory.

        Return None if key not in the dictionary.
    '''
    if key not in mem_dict: return None
    key_queue.remove(key)
    key_queue.insert(0, key) # Place the key to the most recent used
    return mem_dict[key]

def RandomReplacement(size: int) -> None: #random
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
    ''' Try to clean up a space for a incoming file.
        Return if the cleanup is successful
    '''
    capacity = Config['capacity']
    policy = Config['policy']
    if filesize + size <= capacity: return False
    if policy == "random":
        RandomReplacement(size)
    else:
        LeastRecentlyUsed(size)
    return True


"""Funcitions"""

def invalidateKey(key):
    debuginfo = mem_dict.pop(key, "no such key")
    print(debuginfo)
    response = webapp.response_class(
        response=json.dumps("ok"),
        status=200,
        mimetype='application/json',
    )
    return response

def refreshConfiguration():
    get_config_info()
    response = webapp.response_class(
        response=json.dumps(Config),
        status=200,
        mimetype='application/json',
    )
    return response

def subPut(key,value):
    """do something with key"""
    print(key,value)
    invalidateKey(key)
    response = webapp.response_class(
        response=json.dumps(key+value),
        status=200,
        mimetype='application/json',
    )
    return response


def subGET(key):
    """do something"""
    print("get")
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

#test page

@webapp.route('/testread',methods=['POST', 'GET'])
def TEST():
    return refreshConfiguration()


Config = {'capacity': 20, 'policy': 'LRU'}
mem_add("a", bytes("aaaaa", 'utf-8'))
mem_add("b", bytes("bbbbb", 'utf-8'))
mem_add("c", bytes("bbbbb", 'utf-8'))
mem_add("d", bytes("bbbbb", 'utf-8'))
mem_add("e", bytes("bbbbb", 'utf-8'))
mem_add("f", bytes("abcde", 'utf-8'))
print(mem_dict)
print(key_queue)
mem_get("d")
print(mem_dict)
print(key_queue)


