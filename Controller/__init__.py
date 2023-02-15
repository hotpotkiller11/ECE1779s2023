from flask import Flask
from Controller.CacheController import CacheController

webapp = Flask(__name__)
memcache_list = ["127.0.0.1:7000", "127.0.0.1:7001"]

from Controller import main

controller = CacheController(memcache_list)
