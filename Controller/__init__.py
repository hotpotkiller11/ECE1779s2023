from flask import Flask
from Controller.CacheController import CacheController

webapp = Flask(__name__)
memcache_list = ["http://127.0.0.1:5000/memcache1", "http://127.0.0.1:5000/memcache2"]
control = CacheController(memcache_list)

from Controller import main
