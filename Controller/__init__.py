from flask import Flask
from Controller.CacheController import CacheController
import boto3

webapp = Flask(__name__)
memcache_id_list = ['i-06abd9e9282fc4a6f', 'i-0243a81799646f826',
                    'i-0c5bd964679b374ce', 'i-09b9e45c8a0364959',
                    'i-03e312d7cd17fa896', 'i-0de7d539f52225815',
                    'i-0a1e0efb0b5698881', 'i-0a1e0efb0b5698881']
memcache_ip_list = []
for node_id in memcache_ip_list:
    ec2=boto3.client('ec2')
    ip = ec2.describe_instances(InstanceIds=[node_id])['Reservations'][0]['Instances'][0]['PrivateDnsName']
    memcache_ip_list.append(ip)
    
control = CacheController(memcache_ip_list)
# control.modify_pool_size(1)
print("Loading private ip from instance id")
print(memcache_id_list)
print(memcache_ip_list)

from Controller import main
