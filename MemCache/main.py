
from flask import  request, g, Response
from datetime import datetime
from MemCache import webapp
import random
import mysql.connector
from MemCache.config import db_config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import json



"""Global variables"""
global Config

"""statistical info"""
global filesize # Size of the current figures in cache memory (unit: byte)
miss = 0
hit = 0
reqs = 0
total_reqs = 0
total_miss = 0
total_hit = 0
stat_list = [] # (hit, miss) queue, update every 5 seconds


"""mem cache structure"""
mem_dict = {}
key_queue = [] # LRU list, from the most recent use to the least recent use

"""DB config """
def init_db():
    """
    initialization database
    :return: database initialization
    """

    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    """
    init step 2
    :return: database
    """
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
    """
    get the information of the configuration
    :return: config dictionary
    """
    cnx = get_db()
    query = '''SELECT capacity, policy
                    FROM backend_config where id = (
        select max(id) FROM backend_config);'''
    cursor = cnx.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    # cnx.close() This might cause failure
    global Config
    print(rows[0][0],rows[0][1])
    Config = {'capacity': rows[0][0], 'policy': rows[0][1]}

def RandomReplacement(size: int) -> None: #random
    """
    randonreplacement policy cache
    :param size: the size of the cache
    :return: NaN
    """
    global filesize
    capacity = Config['capacity']
    while filesize + size > capacity:
        remove_index = random.randint(0, len(key_queue) - 1)
        removed_key = key_queue.pop(remove_index)
        removed_file = mem_dict.pop(removed_key)
        filesize -= len(removed_file['file'])


def LeastRecentlyUsed(size: int) -> None: #LRU
    """
    least recently used policy
    :param size: the size of the cache
    :return: NaN
    """
    global filesize
    capacity = Config['capacity']
    while filesize + size > capacity:
        removed_key = key_queue.pop() # The last one in the LRU list will be removed
        removed_file = mem_dict.pop(removed_key)
        filesize -= len(removed_file['file'])


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
    mem_dict[key] = {"file": file, "last_access": datetime.now()}
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
    mem_dict[key]["last_access"] = datetime.now()
    return mem_dict[key]["file"]

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
    filesize -= len(removed["file"]) # decrease size
    return True

"""Funcitions"""

def invalidateKey(key):
    """
    call mem_invalidate(key) to perform key invalidation
    :param key: the key to be invalidate
    :return: JSON response
    """
    global reqs
    reqs += 1
    print("invalidate key")
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
    """
    read the configuration info
    :return: JSON response
    """
    global reqs
    reqs += 1
    print("refresh configuration")
    get_config_info()   #configuration refresh, read in refresh
    mem_cleanup(0) # clean up mem until maximum capacity reached
    response = webapp.response_class(
        response=json.dumps(Config),
        status=200,
        mimetype='application/json',
    )
    return response

def subPUT(key,value):
    """
    put the key in to the cache
    :param key: the key given by user
    :param value: the file content
    :return: JSON response
    """
    global reqs
    reqs += 1
    print("put")
    res = mem_add(key, value)
    # print(res)
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response

def subPUTLIST(files: list) -> Response:
    """
    Put a list of files into the cache
    :param key: the key given by user
    :param value: the file content
    :return: JSON response
    """
    global filesize
    global mem_dict
    global key_queue
    print("put list")
    capacity = Config['capacity']
    # Ordered merge sort
    new_key_queue = []
    new_mem_dict = {}
    filesize = 0 # Set it back to 0
    for file in files:
        key = file.pop("key")
        s = file["last_access"]
        print(s)
        file["last_access"] = datetime.strptime(s[:26], '%Y-%m-%d %H:%M:%S.%f')
        if (len(key_queue) > 0): # if previous key queue not depleted
            key_old = key_queue[0] # peek the head of the old key queue
            while file["last_access"] <= mem_dict[key_old]["last_access"]: # key that previously in the node is newer
                # store a element previously in the node
                size = len(mem_dict[key_old]["file"])
                if size + filesize > capacity: break
                new_key_queue.append(key_old)
                new_mem_dict[key_old] = mem_dict[key_old]
                filesize += size
                key_old = key_queue.pop(0) # remove this element from the previous key queue
                # grab new element if not empty
                if len(key_queue) == 0: break
                key_old = key_queue[0]
                
        # Store a file from incoming file list if key is newer or previous key_queue has depleted
        size = len(file["file"])
        if size + filesize > capacity: break
        new_key_queue.append(key)
        new_mem_dict[key] = file
        filesize += size
    else: # All file in incoming file list are stored but not reach the capacity limit yet
        for key_old in key_queue:
            # Try to store all the keys in previous key queue until it reach the capacity limit
            size = len(mem_dict[key_old]["file"])
            if size + filesize > capacity: break
            new_key_queue.append(key_old)
            new_mem_dict[key_old] = mem_dict[key_old]
            filesize += size
    
    # Update the storage
    mem_dict  = new_mem_dict
    key_queue = new_key_queue
        
    # print(res)
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response


def subGET(key):
    """
    perform a get request, calculate the hit and miss info
    :param key: the key to be get
    :return: JSON response
    """
    global hit
    global miss
    global reqs
    reqs += 1
    print("get")
    img = mem_get(key)
    if img is not None:
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
        hit += 1
    else:
        response = webapp.response_class(
            response=json.dumps("MISS"),
            status=404,
            mimetype='application/json',
        )
        miss += 1
    return response

def subCLEAR():
    """
    call  mem_clear() to clean the cache
    :return: JSON response
    """
    global reqs
    reqs += 1
    print("clear")
    mem_clear()
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response

def subDROP(keys: list) -> Response:
    for key in keys:
        mem_invalidate(key)
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response
        

def get_all() -> Response:
    """ Get all files the node. Return all stored data.
        The files will be returned in least recent used 
        order from the newest to oldest

    Returns:
        Response: Stored files
    """
    files = []
    
    for key in key_queue:
        d = {"key": key}
        d.update(mem_dict[key]) # append mem_dict element with its key
        files.append(d)
    
    response = webapp.response_class(
        response=json.dumps(files, default=str),
        status=200,
        mimetype='application/json',
    )
    
    return response
    

"interfaces"

@webapp.route('/', methods=['POST', 'GET'])
def welcome():
    #   base page unused test only
    return "Test page--welcome to back end"

@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    value = request.json["value"]
    return subPUT(key,value)

@webapp.route('/put/list', methods=['POST', 'GET'])
def PUTLIST():
    files = request.json
    return subPUTLIST(files)

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
    key = request.json['key']
    return invalidateKey(key)

@webapp.route('/keys',methods=['GET'])
def keys():
    """
    list all the keys in the memcache
    :return: JSON response
    """

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

@webapp.route('/refresh', methods= ['POST' , 'GET'])
def REFRESH():
    return refreshConfiguration()

@webapp.route("/get/all", methods= ['POST' , 'GET'])
def GETALL():
    return get_all()

@webapp.route("/drop", methods= ['POST' , 'GET'])
def DROP():
    keys = request.json["keys"]
    print(keys)
    return subDROP(keys)
