import boto3
from botocore.args import logger
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
#create ec2 instance
ec2.create_instances(ImageId='ami-080ff70d8f5b80ba5', MinCount=1, MaxCount=1, InstanceType='t2.small')#, SubnetId='subnet-4727f330')

#instances = ec2.instances.all()
def checkAllInstance():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print(instance.id, instance.instance_type)

    # instance status
    for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
        print(status)

def terminateInstance():
    instances = ec2.instances.all
    for instance in instances:
        print("terminating",instance.id, instance.instance_type)
        ec2.instances.filter(InstanceIds=[instance.id]).terminate()
    ec2.instances.terminate()#stop all just in case u know what i mean

def startInstance(id):
    instance = ec2.instances.filter(InstanceIds=[id])
    if instance is None:
        logger.info("No instance to start.")
        return 0
    try:
        response = instance.start()
        instance.wait_until_running()
    except ClientError as err:
        logger.error(
                    "Couldn't start instance %s. Here's why: %s: %s", instance.id,
                    err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    else:
        return response

def stop(id):
    """
    Stops an instance and waits for it to be in a stopped state.

    :return: The response to the stop request.
    """
    instance = ec2.instances.filter(InstanceIds=[id])
    if instance is None:
            logger.info("No instance to stop.")
            return
    try:
            response = instance.stop()
            instance.wait_until_stopped()
    except ClientError as err:
            logger.error(
                "Couldn't stop instance %s. Here's why: %s: %s", instance.id,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
    else:
        return response



terminateInstance()