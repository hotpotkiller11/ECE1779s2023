from datetime import datetime, timedelta
from botocore.args import logger
from botocore.exceptions import ClientError
import boto3
#list of matrix name
# CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn, NetworkPacketsOut, DiskWriteBytes, DiskReadBytes,
# DiskWriteOps, DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed, StatusCheckFailed_Instance,
# StatusCheckFailed_System

class CloudWatchWrapper:
    """Encapsulates Amazon CloudWatch functions."""
    def __init__(self, cloudwatch_resource):
        """
        :param cloudwatch_resource: A Boto3 CloudWatch resource.
        """
        self.cloudwatch_resource = cloudwatch_resource

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

    def list_metrics(self, namespace, name, recent=False):
        """
        Gets the metrics within a namespace that have the specified name.
        If the metric has no dimensions, a single metric is returned.
        Otherwise, metrics for all dimensions are returned.

        :param namespace: The namespace of the metric.
        :param name: The name of the metric.
        :param recent: When True, only metrics that have been active in the last
                       three hours are returned.
        :return: An iterator that yields the retrieved metrics.
        """
        try:
            kwargs = {'Namespace': namespace, 'MetricName': name}
            if recent:
                kwargs['RecentlyActive'] = 'PT3H'  # List past 3 hours only
            metric_iter = self.cloudwatch_resource.metrics.filter(**kwargs)
            logger.info("Got metrics for %s.%s.", namespace, name)
        except ClientError:
            logger.exception("Couldn't get metrics for %s.%s.", namespace, name)
            raise
        else:
            return metric_iter
    def list_statistics(self, metric_name, period):
        """
        :param metric_name: see listed commands above
        :param period: looping time in s
        :return: json stat
        """
        try:
            stat = client.get_metric_statistics(
                Period=period,
                StartTime=datetime.utcnow() - timedelta(seconds=60 * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
                MetricName=metric_name,
                Namespace='AWS/EC2',  # Unit='Percent',
                Statistics=['Maximum'],
                Dimensions=[{'Name': 'InstanceId', 'Value': 'i-09c738fc558cb24a6'}])
        except ClientError:
            logger.exception("Couldn't get statistics for %s.%s.", metric_name, period + "")
            raise
        return stat

if __name__ == '__main__':
    client = boto3.client('cloudwatch')
    statManager = CloudWatchWrapper(client)
    print(statManager.list_statistics('CPUUtilization',1*60))
