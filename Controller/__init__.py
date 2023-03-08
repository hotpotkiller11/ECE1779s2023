from flask import Flask
from Controller.CacheController import CacheController
from Controller.config import memcache_id_list
import boto3


webapp = Flask(__name__)

memcache_ip_list = []
for node_id in memcache_id_list:
    ec2=boto3.client('ec2')
    ip = ec2.describe_instances(InstanceIds=[node_id])['Reservations'][0]['Instances'][0]['PrivateDnsName']
    memcache_ip_list.append("http://" + ip + ":5000")
    
control = CacheController(memcache_ip_list)
# control.modify_pool_size(1)
print("Loading private ip from instance id")
print(memcache_id_list)
print(memcache_ip_list)

#statistic
global T_max_miss
T_max_miss = 0.8#   init value
global T_max_miss
T_max_miss = 0.2 #   init value
global expand
global shrink

from Controller import main
