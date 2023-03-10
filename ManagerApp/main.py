from flask import render_template, request, json
from ManagerApp import webapp, key_path, db_connect, backend
from ManagerApp.key_path import get_path_by_key
from ManagerApp.config import IMAGE_FORMAT 
from ManagerApp.db_connect import get_db
from botocore.config import Config
import base64
import os
import requests
import boto3

config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)
s3 = boto3.client('s3',config=config)
@webapp.route('/')
def home():
    return render_template("home.html")

# msg pages
@webapp.route('/success')
def success():
    # msg = request.args.get('msg')
    # return render_template("success.html", msg=msg)
    return render_template("success.html")

@webapp.route('/failure')
def failure():
    # msg = request.args.get('msg')
    # return render_template("failure.html", msg=msg)
    return render_template("error.html")

# favicon

@webapp.route('/favicon.ico')
def favicon():
    return webapp.send_static_file('favicon.ico')

# function 1: show all keys

@webapp.route('/keys/delete', methods=['GET'])
def all_key_delete():
    """
    clean up all key
    :return: error or success info html
    """
    result = key_path.delete_all_key_path_term()
    result2 = clear_figure_S3()
    res = requests.get(backend + '/clear') # get keys list
    if res.status_code != 200: print("memcache deletion failed")
    if result and result2 == True:
        # also call memcache to remove all cache terms
        return render_template("success.html", msg = "All keys deleted.")
    elif result == False:
        return render_template("error.html", msg = "Deletion failed, database issues!")
    else:
        return render_template("error.html", msg = "Deletion failed, local file system issues!")

@webapp.route('/memory', methods=['GET'])
def memory_inspect():
    """
    configuration of the memcache
    :return: success/error html
    """
    res = requests.get(backend + '/keys') # get keys list
    if (res.status_code == 200):
        nodes = res.json()['nodes']
        n = res.json()['count']
        size = res.json()['total_size']
        # Convert size of each node
        for node in nodes:
            if node["activate"]:
                node["size"] = unit_convertor(node["size"])
    else:
        return render_template("error.html", msg = "Cannot connect to the memcache server.")
    res = requests.get(backend + "/get_auto_params") # get auto-scaler params
    if (res.status_code == 200):
        auto = res.json()['auto']
        max_miss = res.json()['max_miss']
        min_miss = res.json()['min_miss']
        expand = res.json()['expand']
        shrink = res.json()['shrink']
        auto_scaler = {"auto": auto,
                       "max_miss": max_miss,
                       "min_miss": min_miss,
                       "expand": expand,
                       "shrink": shrink}
    else:
        return render_template("error.html", msg = "Cannot get auto-scaler status.")
    try:
        db = get_db()
        query = '''SELECT capacity, policy
                        FROM backend_config where id = (
            select max(id) FROM backend_config);'''
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        capacity = rows[0][0]
        policy = rows[0][1]
    except Exception as e:
        print(e)
        return render_template("error.html", msg = "Cannot connect to the memcache server.")
    return render_template("memory.html", nodes = nodes, n = n, size = unit_convertor(size),
        capacity = unit_convertor(capacity), policy = policy, auto_scaler = auto_scaler)

def unit_convertor(byte: int) -> str:
    """
    converting size, matching the size unit
    :param byte: size given
    :return: size in specific unit
    """
    unit = ['B', 'KB', 'MB', 'GB', 'TB']
    u = 0
    while byte >= 1024:
        byte /= 1024
        u += 1
        if u >= len(unit) - 1: break
    return "%.2f %s" % (byte, unit[u])


@webapp.route('/memory/clear')
def mem_key_delete():
    """
    clean up keys
    :return: success/error html
    """
    res = requests.get(backend + '/clear') # get keys list
    if (res.status_code == 200):
        return render_template("success.html", msg = "Cache deleted.")
    else:
        return render_template("error.html", msg = "Cache clear failed: error %d" % res.status_code)

@webapp.route('/memory/set', methods=['POST'])
def mem_config_set():
    """
    set up the memcache configuration
    :return: success/error html
    """
    capacity = float(request.form.get('capacity'))
    unit = request.form.get('unit')
    if unit == "KB": capacity *= 1024
    elif unit == "MB": capacity *= 1024 * 1024
    policy = request.form.get('policy')
    db = db_connect.get_db()
    query = 'INSERT INTO `backend_config` (`capacity`, `policy`) VALUES (%d, "%s")' % (capacity, policy)
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
        # db.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        # db.close()
        return render_template('error.html', msg = "Database insertion failed")
    res = requests.get(backend + '/refresh') # get keys list
    if (res.status_code == 200):
        return render_template("success.html", msg = "Configuration updated")
    else:
        return render_template("error.html", msg = "Memcache update failed: error %d" % res.status_code)
    
@webapp.route('/memory/pool', methods=['POST'])
def mem_pool_set():
    active = int(request.form.get('new_active'))
    res = requests.post(backend + '/pool', json = {"new_active": active})
    if (res.status_code == 200):
        return render_template("success.html", msg = "Configuration updated")
    else:
        return render_template("error.html", msg = "Memcache update failed: error %d" % res.status_code)

@webapp.route('/memory/auto', methods=['POST'])
def auto_on_off():
    active = request.form.get("auto", type=bool)
    if active == None:
        response = webapp.response_class(
        response=json.dumps("Bad request"),
        status=400,
        mimetype='application/json',
        )
        return response
    res = requests.post(backend + '/auto', json = {"auto": active})
    if res.status_code == 200:
        response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
        )
        return response
    else:
        response = webapp.response_class(
        response=json.dumps("Internal error"),
        status=500,
        mimetype='application/json',
        )
        return response
    
@webapp.route("/memory/auto_params", methods=['POST'])
def auto_params():
    max_miss = request.form.get("max_miss", type=float) / 100 # percentage to decimal
    min_miss = request.form.get("min_miss", type=float) / 100 # percentage to decimal
    if(max_miss < min_miss):
        return render_template("error.html", msg = "max miss rate < min miss rate")
    shrink = request.form.get("shrink")
    expand = request.form.get("expand")
    res = requests.post(backend + "/auto_params", 
                  json = {"max_miss": max_miss, "min_miss": min_miss, "shrink": shrink, "expand": expand})
    if res.status_code == 200:
        return render_template("success.html", msg = "Auto scaler parameters updated")
    else:
        return render_template("error.html", msg = "Parameters update failed. Error code = %d" % (res.status_code))

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    """
    handel 404 info page
    :param e: exception
    :return: 404.html
    """
    return render_template('404.html')

def clear_figure_S3():
    """
    clear all images in S3 bucket
    :return: bool
    """
    s3_clear = boto3.resource('s3',config=config)
    bucket = s3_clear.Bucket('ece1779-ass2-bucket1')
    bucket.objects.all().delete()
    return True
