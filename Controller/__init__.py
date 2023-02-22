from flask import Flask
from Controller.CacheController import CacheController

webapp = Flask(__name__)
memcache_list = ["http://127.0.0.1:7002", "http://127.0.0.1:7001"]
control = CacheController(memcache_list)
control.modify_pool_size(2)

from Controller import main
