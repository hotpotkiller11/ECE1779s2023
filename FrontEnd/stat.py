from datetime import datetime, timedelta
from FrontEnd.db_connect import get_db
from FrontEnd import webapp
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
from toolAWS import cloudWatch
import boto3
from datetime import datetime

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
            hit_rate[time] = miss[time] / total
    
    hit_xy = []
    miss_xy = []
    req_xy = []
    size_xy = []
    count_xy = []
    
    # Averaged scalers
    
    time_list = list(miss_rate.keys())
    time_list.sort() #order the time list (asc)
    
    for time in time_list:
        formatted_time = time.strftime("%Y-%b-%d %H:%M:%S") # format time
        hit_xy.append({'x': formatted_time, 'y': hit_rate[time]})
        miss_xy.append({'x': formatted_time, 'y': miss_rate[time]})
        req_xy.append({'x': formatted_time, 'y': req[time]})
    
    # Separated scalers
    
    for i in range(len(results["size"])):
        size = []
        count = []
        for j in range(len(results["size"][i])):
            size.append({"x": results["size"][i][j]["Timestamp"], "y": results["size"][i][j]["Average"]})
            count.append({"x": results["items"][i][j]["Timestamp"], "y": results["items"][i][j]["Average"]})
        size_xy.append(size)
        count_xy.append(count)
        
    return str(size_xy)
