import os
from datetime import datetime, timedelta
from botocore.args import logger
from botocore.exceptions import ClientError
import boto3
import subprocess
#list of matrix name
# CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn, NetworkPacketsOut, DiskWriteBytes, DiskReadBytes,
# DiskWriteOps, DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed, StatusCheckFailed_Instance,
# StatusCheckFailed_System
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

    def create_metric_alarm(
            self, metric_namespace, metric_name, alarm_name, stat_type, period,
            eval_periods, threshold, comparison_op):
        """
        Creates an alarm that watches a metric.

        :param metric_namespace: The namespace of the metric.
        :param metric_name: The name of the metric.
        :param alarm_name: The name of the alarm.
        :param stat_type: The type of statistic the alarm watches.
        :param period: The period in which metric data are grouped to calculate
                       statistics.
        :param eval_periods: The number of periods that the metric must be over the
                             alarm threshold before the alarm is set into an alarmed
                             state.
        :param threshold: The threshold value to compare against the metric statistic.
        :param comparison_op: The comparison operation used to compare the threshold
                              against the metric.
        :return: The newly created alarm.
        """
        try:
            metric = self.cloudwatch_resource.Metric(metric_namespace, metric_name)
            alarm = metric.put_alarm(
                AlarmName=alarm_name,
                Statistic=stat_type,
                Period=period,
                EvaluationPeriods=eval_periods,
                Threshold=threshold,
                ComparisonOperator=comparison_op)
            logger.info(
                "Added alarm %s to track metric %s.%s.", alarm_name, metric_namespace,
                metric_name)
        except ClientError:
            logger.exception(
                "Couldn't add alarm %s to metric %s.%s", alarm_name, metric_namespace,
                metric_name)
            raise
        else:
            return alarm

    def list_statistics(self, metric_name, period):
        """
        :param metric_name: see listed commands above
        :param period: looping time in s
        :return: json stat
        """
        try:
            stat = self.cloudwatch_resource.get_metric_statistics(
                Period=period,
                StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
                MetricName=metric_name,
                Namespace='1779/STATISTIC',  # Unit='Percent',
                Statistics=['Maximum'],
                Dimensions=[{'Name': 'InstanceId', 'Value': 'i-09c738fc558cb24a6'}])
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", metric_name, period + "")
            raise
        return stat

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

    def monitor_missmean(self, metric_name = 'miss_rate', intervals=60, period=60, EC2id=[]):# add id list in
        misslist = []
        for i in EC2id:
            stat = self.cloudwatch_resource.get_metric_statistics(
                Period=period,
                StartTime=datetime.utcnow() - timedelta(seconds=intervals),
                EndTime=datetime.utcnow() - timedelta(seconds=intervals),
                MetricName=metric_name,
                Namespace='1779/STATISTIC',
                Statistics=['Maximum'],
                Unit='Percent',
                Dimensions=[{'Name': 'InstanceId', 'Value': i}])
            misslist.appent(stat)
        return misslist

if __name__ == '__main__':
    client = boto3.client('cloudwatch')
    statManager = CloudWatchWrapper(client)
    #print(statManager.list_statistics('CPUUtilization',1*60))
    statManager.post_req(0)

