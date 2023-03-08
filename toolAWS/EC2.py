import boto3
from botocore.args import logger
from botocore.exceptions import ClientError
class EC2Wrapper:
    def __init__(self, ec2_resource):
        self.ec2_resource = ec2_resource

    def checkAllInstance(self):
        """
        get all running instance
        :return: instance id list
        """
        instanceID = []
        instances = self.ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            instanceID.append(instance.id)
            #print(instance.id, instance.instance_type)
        #for status in self.ec2_resource.meta.client.describe_instance_status()['InstanceStatuses']:
        #    print(status)

        return instanceID

    def terminateInstance(self):
        """
        terminate all instance
        :return:
        """
        instances = self.ec2_resource.instances.all
        for instance in instances:
            print("terminating",instance.id, instance.instance_type)
            self.ec2_resource.instances.filter(InstanceIds=[instance.id]).terminate()
        #self.ec2_resource.instances.terminate()

    def startInstance(self,id):
        """
        start instance by id
        :return: response
        """
        instance = self.ec2_resource.instances.filter(InstanceIds=[id])
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

    def stop(self, id):
        """
        Stops an instance and waits for it to be in a stopped state.
        :return: The response to the stop request.
        """
        instance = self.ec2_resource.instances.filter(InstanceIds=[id])
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

if __name__ == '__main__':
    ec2 = boto3.resource('ec2')

    # create ec2 instance
    #ec2.create_instances(ImageId='ami-080ff70d8f5b80ba5', MinCount=1, MaxCount=1,
    #                     InstanceType='t2.small')  # , SubnetId='subnet-4727f330')
    #terminateInstance()
# instances = ec2.instances.all()