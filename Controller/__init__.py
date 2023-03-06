from flask import Flask
from Controller.CacheController import CacheController

webapp = Flask(__name__)
memcache_list = ["http://172.31.91.73:5000", "http://172.31.59.184:5000"]
control = CacheController(memcache_list)
# control.modify_pool_size(1)

from Controller import main
