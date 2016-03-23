"""
This AWS Lambda function is intended to be invoked via a lifecycle hook
from a new instance launch. New instances will fetch the latest codepipeline
artifact from S3 and execute it with runcommand. After runcommand is invoked,
complete the lifecycle action.
chavisb@amazon.com
v0.0.1
"""

import logging
import boto3
import datetime
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#assume we're always using a pipeline name GARLC
pipeline_name = 'GARLC'

def find_bucket(pipeline_name):
    """
    find S3 bucket that codedeploy uses and return bucket name
    """
    try:
        codepipeline = boto3.client('codepipeline')
        pipeline = codepipeline.get_pipeline(name=pipeline_name)
        return pipeline['pipeline']['artifactStore']['location']
    except (IOError, ClientError, KeyError) as err:
        LOGGER.error(err)
    return False

#find newest artifact in S3 bucket
def find_newest_artifact(bucket):
    """
    find and return the newest artifact in codepipeline bucket
    TODO: implement boto collections to support more than 1000 artifacts per bucket
    """
    try:
        s3 = boto3.client('s3')
        objects = s3.list_objects(Bucket=bucket)
        list = [i['LastModified'] for i in objects['Contents']]
        return sorted(list[-1])
    except (IOError, ClientError, KeyError) as err:
        LOGGER.error(err)
    return False

#do runcommand stuff
def ssm_commands(artifact):
    """
    Builds commands to be sent to SSM (Run Command)
    """
    # TODO
    # Error handling in the command generation
    utc_datetime = datetime.datetime.utcnow()
    timestamp = utc_datetime.strftime("%Y%m%d%H%M%S")
    return [
        'aws configure set s3.signature_version s3v4',
        'aws s3 cp {0} /tmp/{1}.zip --quiet'.format(artifact, timestamp),
        'unzip -qq /tmp/{0}.zip -d /tmp/{1}'.format(timestamp, timestamp),
        'bash /tmp/{0}/generate_inventory_file.sh'.format(timestamp),
        'ansible-playbook -i "/tmp/inventory" /tmp/{0}/ansible/playbook.yml'.format(timestamp)
    ]

def log_event(event):
    """Logs event information for debugging"""
    LOGGER.info("====================================================")
    LOGGER.info(event)
    LOGGER.info("====================================================")

#Grab the instance ID out of the "event" dict sent by cloudwatch events
#We are not using this function right now, not sure if necessary
def get_instance_id(event):
    try:
        return event['detail']['EC2InstanceId']
    except KeyError as err:
        LOGGER.error(err)
    return False

def build_lifecycle_args(event):
    try:
        hookname = event['detail']['LifecycleHookName']
        groupname = event['detail']['AutoScalingGroupName']
        token = event['detail']['LifecycleActionToken']
        return hookname, groupname, token
    except (IOError, ClientError, KeyError) as err:
        LOGGER.error(err)
    return False


def handle(event, _context):
    """Lambda Handler"""
    log_event(event)
try:
#pass find_newest_artifact() the bucket name output from find_bucket()
    artifact = find_newest_artifact(find_bucket(pipeline_name))
except (IOError, ClientError, KeyError) as err:
    LOGGER.error(err)
try:
#tell runcommand the artifact name
    ssm_commands(artifact)
except (IOError, ClientError, KeyError) as err:
    LOGGER.error(err)
try:
#signal lifecycle action
    hookname, groupname, token = build_lifecycle_args(event)
    autoscaling = boto3.client('autoscaling')
    autoscaling.complete_lifecycle_action(
        LifecycleHookName=hookname,
        AutoScalingGroupName=groupname,
        LifecycleActionToken=token,
        LifecycleActionResult="CONTINUE"
        )
except (IOError, ClientError, KeyError) as err:
    LOGGER.error(err)
