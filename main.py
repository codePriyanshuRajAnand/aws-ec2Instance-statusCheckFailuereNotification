# Import required packages
import boto3

# Initialize resorces, clients & variables required
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

InstanceIds = []

# Get all InstanceIds in the region
for instance in ec2.instances.all():
    InstanceIds.append(instance.id)

# Call API for getting Instance status report
response = ec2_client.describe_instance_status(
    InstanceIds=InstanceIds
)

# Publish SNS message to trigger MoogsoftLambda for creating Incident...
def sendAlarm(instanceId):
    instanceName = ec2.Instance(instanceId).tags[0]['Value']
    print(f"Sending Alarm for {instanceName} ({instanceId})...")
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='<YOUR SNS TOPIC ARN>',
        Message=f'EC2 Instance {instanceName} ({instanceId} has one or more status check failed.',
        Subject=f'EC2 Instance {instanceName} ({instanceId} has one or more status check failed.'
    )
    if(response['ResponseMetadata']['HTTPStatusCode']==200):
        print("Alarm Sent...")
    else:
        print("FAILED to send Alarm...")

# Test Notification...
def notify(instanceId):
    instanceName = ec2.Instance(instanceId).tags[0]['Value']
    sns = boto3.client('sns')
    response = sns.publish(
        TopicArn='<YOUR SNS TOPIC ARN>',
        Message=f'EC2 Instance {instanceName} ({instanceId} is running fine...',
        Subject=f'EC2 Instance {instanceName} ({instanceId} Status Check'
    )
    if(response['ResponseMetadata']['HTTPStatusCode']==200):
        print("Notification Sent...")
    else:
        print("FAILED to send Notification...")


# If Response is 200 then loop through all instances and validate status of every instance
if(response['ResponseMetadata']['HTTPStatusCode']==200):
    print("Connected to EC2 Services successfully...")
    for instance in response['InstanceStatuses']:
        if(instance['InstanceStatus']['Status']=='ok' and instance['SystemStatus']['Status']=='ok' and instance['AttachedEbsStatus']['Status']=='ok'):
            print(instance['InstanceId']+" is running fine...")
            notify(instance['InstanceId'])
        else:
            sendAlarm(instance['InstanceId'])

def lambda_handler(event, context):
    pass
