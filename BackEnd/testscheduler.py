from BackEnd import webapp
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g
miss = 0
hit = 0
key_queue = 0
filesize = 0
numOfreq = 0
import datetime



def write_stat():
    total = miss+hit
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    #print((now, miss/total, hit/total, len(key_queue), filesize, numOfreq))
    #   rows = cursor.fetchall()



with webapp.app_context():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=write_stat, trigger="interval", seconds=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    print("enter")