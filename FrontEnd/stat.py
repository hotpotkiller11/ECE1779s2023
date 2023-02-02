from datetime import datetime, timedelta
from FrontEnd.db_connect import get_db
from FrontEnd import webapp
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template
import atexit

def get_stats() -> list[dict]:
    result = []

    now = datetime.now()
    boundary = now - timedelta(minutes = 10) # Get data of last 10 minutes
    boundary = boundary.strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()

    cursor = db.cursor()
    query = "SELECT `hit`, `miss`, `request_count`, `size`, `picture_count` FROM `backend_statistic` WHERE `timestamp` > '%s' " % boundary # ordered by timestamp by default
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    for r in rows:
        point = {}
        point["hit_rate"] = r[0] / max(r[0] + r[1], 1)
        point["miss_rate"] = r[1] / max(r[0] + r[1], 1)
        point["size"] = r[3]
        point["count"] = r[4]
        point["req"] = r[2]
        result.append(point)
    return result

@webapp.route('/statistic', methods = ['GET','POST'])
# returns the upload page
def stat():
    hit_xy = []
    miss_xy = []
    size_xy = []
    count_xy = []
    req_xy = []
    stat_list = get_stats()
    length = len(stat_list)
    time = (length - 1) * -5
    for p in stat_list:
        hit_xy.append({"x": time, "y": p["hit_rate"]})
        miss_xy.append({"x": time, "y": p["miss_rate"]})
        size_xy.append({"x": time, "y": p["size"]})
        count_xy.append({"x": time, "y": p["count"]})
        req_xy.append({"x": time, "y": p["req"]})
        time += 5

    return render_template("statistic.html", hit_xy = hit_xy, miss_xy = miss_xy, size_xy = size_xy, count_xy = count_xy, req_xy = req_xy)