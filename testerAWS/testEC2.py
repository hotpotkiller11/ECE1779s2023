import boto3

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


terminateInstance()