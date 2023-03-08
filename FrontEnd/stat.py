from datetime import datetime, timedelta
from FrontEnd.db_connect import get_db
from FrontEnd import webapp
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
from toolAWS import cloudWatch
import boto3

cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
statManager = cloudWatch.CloudWatchWrapper(cloudwatch)

def get_stats() :#-> list[dict]:
    """
    get current stats
    :return: list[dict]
    """
    # 3 increment values
    miss = statManager.monitor_stat("miss", "Sum")
    hit = statManager.monitor_stat("hit", "Sum")
    req = statManager.monitor_stat("req", "Sum")
    # 2 scaler values
    size = statManager.monitor_stat("size", "Average")
    items = statManager.monitor_stat("numitem", "Average")
    result = {"miss":  miss,
              "hit":   hit,
              "req":   req,
              "size":  size,
              "items": items}
    return result

@webapp.route('/statistic', methods = ['GET','POST'])
def stat():
    """
    build the statistic list
    :return: html page render
    """
    # hit_xy = []
    # miss_xy = []
    # size_xy = []
    # count_xy = []
    # req_xy = []
    # stat_list = get_stats()
    # length = len(stat_list)
    # time = (length - 1) * -5
    # for p in stat_list:
    #     hit_xy.append({"x": time, "y": p["hit_rate"]})
    #     miss_xy.append({"x": time, "y": p["miss_rate"]})
    #     size_xy.append({"x": time, "y": p["size"]})
    #     count_xy.append({"x": time, "y": p["count"]})
    #     req_xy.append({"x": time, "y": p["req"]})
    #     time += 5

    # return render_template("statistic.html", hit_xy = hit_xy, miss_xy = miss_xy, size_xy = size_xy, count_xy = count_xy, req_xy = req_xy)
    
    return get_stats()