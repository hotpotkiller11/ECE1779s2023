import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import  request, Response
from Controller import webapp, control
import json
import requests

import boto3
from toolAWS.cloudWatch import CloudWatchWrapper
from toolAWS.EC2 import EC2Wrapper
# statistics
cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
statManager = CloudWatchWrapper(cloudwatch)
ec2Manager = EC2Wrapper(ec2)

# auto scale active
Active = False # default, close

def auto_scale():
    """
    read the max and min miss rate
    and shrink/expand rate
    do auto scale function
    Max Miss Rate threshold (average for all nodes in the pool over the past 1 minute) for growing the pool.
    Min Miss Rate threshold (average for all nodes in the pool over the past 1 minute) for shrinking the pool.
    Ratio by which to expand the pool (e.g., expand ratio of 2.0, doubles the number of memcache nodes).
    Ratio by which to shrink the pool (e.g., shrink ratio of 0.5, shuts down 50% of the current memcache nodes).
    :return: None
    """

    if Active:
        with webapp.app_context():

            current_miss = statManager.monitor_miss_rate()
            current_active = len(control.activated_nodes())-1 # not including controller

            if current_miss < T_max_miss and current_miss > T_min_miss:
                print("---no need for scale---")
            elif current_miss > T_max_miss:
                print("---miss rate large, expanding---")
                if current_active*expand >= 8:
                    control.modify_pool_size(8)
                else:
                    control.modify_pool_size(current_active*expand)
            else:
                print("---miss rate samll, shrinking---")
                if current_active*shrink <= 1:
                    control.modify_pool_size(1)
                else:
                    control.modify_pool_size(current_active*shrink)
        print("success looping, current avaliable",(len(control.activated_nodes())-1),control.activated_nodes())#ips
    else:
        pass


with webapp.app_context():
    """
    looping for 60 seconds, doing job auto scale
    """
    # get_config_info()
    """global T_max_miss
    global T_min_miss
    global expand
    global shrink"""
    T_max_miss = 0.8
    T_min_miss = 0.2
    expand = 2
    shrink = 0.5

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=auto_scale, trigger="interval", seconds=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


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

@webapp.route('/invalidatekey', methods=['POST', 'GET'])
def INVALIDATE():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/invalidatekey", json = request.json)
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

@webapp.route('/refresh',methods= ['POST' , 'GET'])
def REFRESH():
    nodes = control.activated_nodes()
    for node in nodes:
        requests.post(node + "/refresh")
    
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/keys',methods=['GET', 'POST'])
def keys():
    result = []
    active_nodes = control.activated_nodes()
    n = 0
    i = 0
    total_size = 0
    for node in active_nodes:
        res = requests.get(node + '/keys') # get keys list
        
        # if (res.status_code == 200):
        keys = res.json()['keys']
        n += len(keys)
        size = res.json()['size']
        total_size += size
        node_stat = {"id": i, "activate": True, "key": keys, "size": size}
        i += 1
        result.append(node_stat)
    
    not_active_nodes = control.not_activated_nodes()
    for node in not_active_nodes:
        node_stat = {"id": i, "activate": False}
        i += 1
        result.append(node_stat)
    
    # Return the response
    response = webapp.response_class(
        response=json.dumps({"count": n, "total_size": total_size, "nodes": result}),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/pool_size',methods=['GET', 'POST'])
def pool_size():
    response = webapp.response_class(
        response=json.dumps({"pool_size": control.pool_size}),
        status=200,
        mimetype='application/json',
    )
    return response
    

@webapp.route('/pool',methods=['POST'])
def pool_config():
    active = request.json["new_active"]
    control.modify_pool_size(active)
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/pool_multi',methods=['POST'])
def pool_multi():
    parameter = request.json["parameter"]
    control.multi_pool_size(parameter)
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response

# Auto scaling settings

def set_auto_scale_param(max_miss = T_max_miss, min_miss = T_min_miss, expand_ratio = expand, shrink_ratio = shrink):
    """ Set auto scale parameters, default to original parameters. 

    Args:
        max_miss (float, optional): _description_. Defaults to T_max_miss.
        min_miss (float_, optional): _description_. Defaults to T_min_miss.
        expand_ratio (float, optional): _description_. Defaults to expand.
        shrink_ratio (float, optional): _description_. Defaults to shrink.
    """
    
    global T_max_miss
    global T_min_miss
    global expand
    global shrink
    
    T_max_miss = max_miss
    T_min_miss = min_miss
    expand = expand_ratio
    shrink = shrink_ratio
    
def auto_scale(active: bool):
    """ Turn on auto scaler or turn off auto scaler

    Args:
        active (bool): true: turn on, false: turn off
    """
    global Active
    Active = active

@webapp.route("/auto", methods=['POST'])
def auto_on_off():
    active = request.form.get("auto")
    auto_scale(active)
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    print("Auto scaler active: " + str(active))
    return response

@webapp.route("/auto_params", methods=['POST'])
def auto_params():
    max_miss = request.form.get("max_miss", T_max_miss, float) # original value if no key found
    min_miss = request.form.get("min_miss", T_min_miss, float)
    expand_ratio = request.form.get("expand", expand, float)
    shrink_ratio = request.form.get("shrink", shrink, float)
    
    set_auto_scale_param(max_miss, min_miss, expand_ratio, shrink_ratio)
    
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    print("New parameters set. " + str(max_miss, min_miss, expand_ratio, shrink_ratio))
    return response
