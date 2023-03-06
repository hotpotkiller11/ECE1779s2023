from flask import Flask
from Controller.CacheController import CacheController

webapp = Flask(__name__)
memcache_list = ["http://172.31.91.73:5000",  "http://172.31.59.184:5000", 
                 "http://172.31.50.65:5000",  "http://172.31.61.162:5000", 
                 "http://172.31.52.177:5000", "http://172.31.60.33:5000",
                 "http://172.31.55.99:5000",  "http://172.31.61.205:5000"]
control = CacheController(memcache_list)
# control.modify_pool_size(1)

from Controller import main
