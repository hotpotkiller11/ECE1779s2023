from flask import Flask

webapp = Flask(__name__)

#statistic
global T_max_miss
global T_min_miss
global expand
global shrink

control = "http://127.0.0.1:5000/controller"

from AutoScaler import main
