import logging
import boto3
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
#assume we're always using a pipeline name GARLC

pipeline_name = 'GARLC'

#find S3 bucket that codedeploy uses
def find_bucket(pipeline_name):
    client = boto3.client('codepipeline')
    pipeline = client.get_pipeline(name = pipeline_name)
    return pipeline_bucket['pipeline']['artifactStore']['location']

#find newest artifact in S3 bucket
def find_newest_artifact(bucket):
    s3 = boto3.client('s3')
    objects = s3.list_objects(Bucket=bucket)
    list = [i['LastModified'] for i in objects['Contents']]
    return sorted(list[-1])

#do runcommand stuff


def log_event(event):
    """Logs event information for debugging"""
    LOGGER.info("====================================================")
    LOGGER.info(event)
    LOGGER.info("====================================================")

#Grab the instance ID out of the "event" dict sent by cloudwatch events
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
#need to include getting S3 bucket and artifact steps
        try:
            hookname, groupname, token = build_lifecycle_args(event)
            autoscaling = boto3.client('autoscaling')
            autoscaling.complete_lifecycle_action(LifecycleHookName=hookname, AutoScalingGroupName=groupname, LifecycleActionToken=token, LifecycleActionResult="CONTINUE")
        except (IOError, ClientError, KeyError) as err:
            LOGGER.error(err)
