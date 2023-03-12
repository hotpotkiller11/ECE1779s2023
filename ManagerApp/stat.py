from datetime import datetime, timedelta
from ManagerApp.db_connect import get_db
from ManagerApp import webapp
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
from toolAWS import cloudWatch
import boto3
from datetime import datetime, timezone

cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
statManager = cloudWatch.CloudWatchWrapper(cloudwatch)

def get_stats() :#-> list[dict]:
    """
    get current stats
    :return: list[dict]
    """
    # 3 increment values

    result = {"miss":  0.5,
              "hit":   0.5,
              "req":   1,
              "size":  100,
              "items": 100}
    return result

def utc_to_local(utc_dt: datetime) -> datetime:
    """ Convert utc datetime to local datetime

    Args:
        utc_dt (datetime): utc datetime

    Returns:
        datetime: local datetime
    """
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

@webapp.route('/statistic', methods = ['GET','POST'])
def stat():
    """
    build the statistic list
    :return: html page render
    """
    # format = "%a, %d %b %Y %H:%M:%S %Z"
    results = get_stats()
    hit = {}
    miss = {}
    req = {}
    for node in results["hit"]:
        for point in node:
            time = point["Timestamp"]
            if time not in hit:
                hit[time] = point["Sum"]
            else:
                hit[time] += point["Sum"]
    for node in results["miss"]:
        for point in node:
            time = point["Timestamp"]
            if time not in miss:
                miss[time] = point["Sum"]
            else:
                miss[time] += point["Sum"]
    for node in results["req"]:
        for point in node:
            time = point["Timestamp"]
            if time not in req:
                req[time] = point["Sum"]
            else:
                req[time] += point["Sum"]
    miss_rate = {}
    hit_rate = {}
    for time in hit.keys():
        total = hit[time] + miss[time] 
        if total == 0:
            hit_rate[time] = 0.0
            miss_rate[time] = 0.0
        else:
            hit_rate[time] = hit[time] / total
            miss_rate[time] = miss[time] / total
    
    hit_xy = []
    miss_xy = []
    req_xy = []
    size_xy = []
    count_xy = []
    
    # Averaged scalers
    
    time_list = list(miss_rate.keys())
    time_list.sort() #order the time list (asc)
    
    for time in time_list:
        formatted_time = utc_to_local(time).strftime("%H:%M") # format time
        hit_xy.append({'x': formatted_time, 'y': hit_rate[time]})
        miss_xy.append({'x': formatted_time, 'y': miss_rate[time]})
        req_xy.append({'x': formatted_time, 'y': req[time]})
    
    # Separated scalers
    
    for i in range(len(results["size"])):
        results["size"][i].sort(key = lambda x: x["Timestamp"]) # reorder the result list with timestamp
        results["items"][i].sort(key = lambda x: x["Timestamp"]) # reorder the result list with timestamp
        size = []
        count = []
        for j in range(len(results["size"][i])):
            size.append({"x": utc_to_local(results["size"][i][j]["Timestamp"]).strftime("%H:%M"),
                         "y": results["size"][i][j]["Average"]})
            count.append({"x": utc_to_local(results["items"][i][j]["Timestamp"]).strftime("%H:%M"),
                          "y": results["items"][i][j]["Average"]})
        size_xy.append(size)
        count_xy.append(count)
        
    return render_template("statistic.html", hit_xy = hit_xy, miss_xy = miss_xy, size_xy = size_xy, count_xy = count_xy, req_xy = req_xy)
