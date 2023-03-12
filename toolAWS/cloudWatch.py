import os
from datetime import datetime, timedelta
from botocore.args import logger
from botocore.exceptions import ClientError
import boto3
import subprocess
from config import memcache_id_list
#list of matrix name
# CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn, NetworkPacketsOut, DiskWriteBytes, DiskReadBytes,
# DiskWriteOps, DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed, StatusCheckFailed_Instance,
# StatusCheckFailed_System
# Now copied from Controller

def getCurrentID() -> str:
    '''
    get the current ec2 id
    return: string id
    '''
    x = subprocess.check_output(['wget', '-q', '-O', '-', 'http://169.254.169.254/latest/meta-data/instance-id'])
    id = x.decode("utf-8")
    print(id)
    return id

class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""
    def __init__(self, cloudwatch_resource):
        self.cloudwatch_resource = cloudwatch_resource
        self.current_id = getCurrentID()

    def post_miss(self, missrate):
        """
            Send Memcache Miss Rate to AWS Cloudwatch. Return a response message.
            missrate: value to send
        """
        instance_id = self.current_id
        # instance_id = 'i-09c738fc558cb24a6'
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        response = self.cloudwatch_resource.put_metric_data(
            MetricData=[{
                'MetricName': 'miss',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_id
                }],
                'Timestamp': now,
                'Unit': 'Count',
                'Value': missrate}],
            Namespace='1779/STATISTIC')
        return response

    def post_hit(self, hitrate):
        """
            Send Memcache Hit Rate to AWS Cloudwatch. Return a response message.
            missrate: value to send
        """
        instance_id = self.current_id
        # instance_id = 'i-09c738fc558cb24a6'
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        response = self.cloudwatch_resource.put_metric_data(
            MetricData=[{
                'MetricName': 'hit',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_id
                }],
                'Timestamp': now,
                'Unit': 'Count',
                'Value': hitrate}],
            Namespace='1779/STATISTIC')
        return response

    def post_numitem(self, numitem):
        """
            Send Memcache items to AWS Cloudwatch. Return a response message.
            numitem: value to send
        """
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        instance_id = self.current_id
        # instance_id = 'i-09c738fc558cb24a6'
        response = self.cloudwatch_resource.put_metric_data(
            MetricData=[{
                'MetricName': 'numitem',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_id
                }],
                'Timestamp': now,
                'Unit': 'Count',
                'Value': numitem}],
            Namespace='1779/STATISTIC')
        return response

    def post_size(self, filesize):
        """
            Send Memcache current file size to AWS Cloudwatch. Return a response message.
            filesize: value to send
        """
        instance_id = self.current_id
        # instance_id = 'i-09c738fc558cb24a6'
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        response = self.cloudwatch_resource.put_metric_data(
            MetricData=[{
                'MetricName': 'size',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_id
                }],
                'Timestamp': now,
                'Unit': 'Count',
                'Value': filesize}],
            Namespace='1779/STATISTIC')
        return response

    def post_req(self,req):
        """
            Send Memcache count to AWS Cloudwatch. Return a response message.
            filesize: value to send
        """
        instance_id = self.current_id
        # instance_id = 'i-09c738fc558cb24a6'
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        response = self.cloudwatch_resource.put_metric_data(
            MetricData=[{
                'MetricName': 'req',
                'Dimensions': [{
                    'Name': 'instance',
                    'Value': instance_id
                }],
                'Timestamp': now,
                'Unit': 'Count',
                'Value': req}],
            Namespace='1779/STATISTIC')
        return response

    def monitor_stat(self, metric_name: str, statistics: str, intervals=30, period = 60, EC2id=memcache_id_list) -> list:# add id list in
        """ Return cloud watch record of cloud watch of the specific ec2 instances

        Args:
            metric_name (str): metric name ('hit'|'miss'|'size'|'numitem'|'req')
            statistics (str): method to present the compression of data points 
                (SampleCount, Average, Sum, Minimum, and Maximum)
            intervals (int, optional): the time to report (unit min). Defaults to 30.
            period (int, optional): resolution of the data points (unit sec). Defaults to 60.
            EC2id (list, optional): a list of . Defaults to all EC2 nodes.

        Returns:
            list: the list of all data points, in the order of EC2id given
        """
        # TODO: implement the last param
        result_list = []
        for id in EC2id:
            stat = self.cloudwatch_resource.get_metric_statistics(
                Period=period,
                StartTime=datetime.utcnow() - timedelta(minutes=intervals),
                EndTime=datetime.utcnow(),
                MetricName=metric_name,
                Namespace='1779/STATISTIC',
                Statistics=[statistics],
                Unit='Count',
                Dimensions=[{'Name': 'instance', 'Value': id}])
            result_list.append(stat['Datapoints'])
        return result_list
    
    def monitor_miss_rate(self, interval = 5) -> float:
        """ Calculate the miss rate of all nodes from last n minutes (n = interval)

        Args:
            interval (int, optional): The time interval (in minutes) to calculate the average miss rate. Defaults to 5.

        Returns:
            float: miss rate calculated (0.0 if no hit or miss)
        """
        result = self.monitor_stat("miss", "Sum", interval, interval * 60)
        # TODO: change the last param
        miss = 0
        for node in result:
            for point in node:
                miss += point["Sum"]
        # print(miss)
        if miss == 0: return 0.0 # No miss or no access, return 0.0 as miss rate
        
        result = self.monitor_stat("hit", "Sum", interval, interval * 60)
        # TODO: change the last param
        hit = 0
        for node in result:
            for point in node:
                hit += point["Sum"]
        # print(hit)
        return miss / (miss + hit) # at least one miss, no div_by_0 error

    def monitor_hit_rate(self, interval = 5) -> float:
            """ Calculate the hit rate of all nodes from last n minutes (n = interval)

            Args:
                interval (int, optional): The time interval (in minutes) to calculate the average hit rate. Defaults to 5.

            Returns:
                float: miss rate calculated (0.0 if no hit or miss)
            """
            result = self.monitor_stat("miss", "Sum", interval, interval * 60)
            # TODO: change the last param
            miss = 0
            for node in result:
                for point in node:
                    miss += point["Sum"]
            # print(miss)
            if miss == 0: return 0.0 # No miss or no access, return 0.0 as miss rate
            
            result = self.monitor_stat("hit", "Sum", interval, interval * 60)
            # TODO: change the last param
            hit = 0
            for node in result:
                for point in node:
                    hit += point["Sum"]
            # print(hit)
            return hit / (miss + hit) # at least one miss, no div_by_0 error
                    


