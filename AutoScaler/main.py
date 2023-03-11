import atexit
import math
from apscheduler.schedulers.background import BackgroundScheduler
from flask import request
from AutoScaler import webapp, control
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

            current_miss = statManager.monitor_miss_rate(interval = 60)
            # Get current setting
            res = requests.post(control + "/pool_size")
            current_active = res.json()["pool_size"] 

            if current_miss < T_max_miss and current_miss > T_min_miss:
                print("---no need for scale---")
            elif current_miss > T_max_miss:
                print("---miss rate large, expanding---")
                if current_active*expand >= 8:
                    requests.post(control + "/pool", json={"new_active": 8})
                else:
                    requests.post(control + "/pool", json={"new_active": math.ceil(current_active*expand)})
            else:
                print("---miss rate samll, shrinking---")
                if current_active*shrink <= 1:
                    requests.post(control + "/pool", json={"new_active": 1})
                else:
                    requests.post(control + "/pool", json={"new_active": math.floor(current_active*shrink)})

        print("success looping, current available",(control.pool_size),control.activated_nodes())#ips
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
    scheduler.add_job(func=auto_scale, trigger="interval", seconds=60)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

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
    active = request.json["auto"]
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
    max_miss = request.json["max_miss"] # original value if no key found
    min_miss = request.json["min_miss"]
    expand_ratio = request.json["expand"]
    shrink_ratio = request.json["shrink"]
    
    set_auto_scale_param(max_miss, min_miss, expand_ratio, shrink_ratio)
    
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    print("New parameters set. " + str([max_miss, min_miss, expand_ratio, shrink_ratio]))
    return response

@webapp.route("/get_auto_params", methods=['GET', 'POST'])
def get_params():
    response = webapp.response_class(
        response=json.dumps({"auto": Active, "max_miss": T_max_miss, "min_miss": T_min_miss,
                             "expand": expand, "shrink": shrink}),
        status=200,
        mimetype='application/json',
    )
    return response
