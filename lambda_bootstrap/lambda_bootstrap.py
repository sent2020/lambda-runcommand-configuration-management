"""
This AWS Lambda function is intended to be invoked via a Cloudwatch Event for a
new intance launch. We get the instance ID from the event message, find our pipeline
bucket, the latest artifact in the bucket, tell the new instance to grab the
artifact, and finally execute it locally via runcommand.
chavisb@amazon.com
v0.0.1
"""
import datetime
import logging
import boto3
from botocore.exceptions import ClientError

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

# assume we're always using a pipeline name GARLC
PIPELINE_NAME = 'GARLC'

def is_a_garlc_instance(instance_id):
    """
    Determine if an instance is GARLC enabled
    """
    filters = [
        {'Name': 'tag:has_ssm_agent', 'Values': ['true', 'True']}
    ]
    try:
        ec2 = boto3.client('ec2')
        instance = ec2.describe_instances(InstanceIds=[str(instance_id)], Filters=filters)
    except ClientError as err:
        LOGGER.error(str(err))
        return False

    if instance:
        return True
    else:
        LOGGER.error(str(instance_id) + " is not a GARLC instance!")
        return False

def find_bucket():
    """
    find S3 bucket that codedeploy uses and return bucket name
    """
    try:
        codepipeline = boto3.client('codepipeline')
        pipeline = codepipeline.get_pipeline(name=PIPELINE_NAME)
        return str(pipeline['pipeline']['artifactStore']['location'])
    except (ClientError, KeyError, TypeError) as err:
        LOGGER.error(err)
        return False

def find_newest_artifact(bucket):
    """
    find and return the newest artifact in codepipeline bucket
    """
    #TODO
    #implement boto collections to support more than 1000 artifacts per bucket
    try:
        aws_s3 = boto3.client('s3')
        objects = aws_s3.list_objects(Bucket=bucket)
        artifact_list = [artifact for artifact in objects['Contents']]
        artifact_list.sort(key=lambda artifact: artifact['LastModified'], reverse=True)
        return 's3://' + bucket + '/' + str(artifact_list[0]['Key'])
    except (ClientError, KeyError) as err:
        LOGGER.error(err)
        return False

def ssm_commands(artifact):
    """
    Builds commands to be sent to SSM (Run Command)
    """
    utc_datetime = datetime.datetime.utcnow()
    timestamp = utc_datetime.strftime("%Y%m%d%H%M%S")
    return [
        'export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/' \
        "latest/dynamic/instance-identity/document | grep region | awk -F\\\" '{print $4}'`",
        'aws configure set s3.signature_version s3v4',
        'aws s3 cp {0} /tmp/{1}.zip --quiet'.format(artifact, timestamp),
        'unzip -qq /tmp/{0}.zip -d /tmp/{1}'.format(timestamp, timestamp),
        'bash /tmp/{0}/generate_inventory_file.sh'.format(timestamp),
        'ansible-playbook -i "/tmp/inventory" /tmp/{0}/ansible/playbook.yml'.format(timestamp)
    ]

def send_run_command(instance_id, commands):
    """
    Sends the Run Command API Call
    """
    try:
        ssm = boto3.client('ssm')
        ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            TimeoutSeconds=300,
            Parameters={
                'commands': commands,
                'executionTimeout': ['120']
            }
        )
        return True
    except ClientError as err:
        LOGGER.error("Run Command Failed!\n%s", str(err))
        return False

def log_event(event):
    """Logs event information for debugging"""
    LOGGER.info("====================================================")
    LOGGER.info(event)
    LOGGER.info("====================================================")

def get_instance_id(event):
    """ Grab the instance ID out of the "event" dict sent by cloudwatch events """
    try:
        return str(event['detail']['instance-id'])
    except (TypeError, KeyError) as err:
        LOGGER.error(err)
        return False

def resources_exist(instance_id, bucket):
    """
    Validates instance_id and bucket have values
    """
    if not instance_id:
        LOGGER.error('Unable to retrieve Instance ID!')
        return False
    elif not bucket:
        LOGGER.error('Unable to retrieve Bucket Name!')
        return False
    else: return True


def handle(event, _context):
    """ Lambda Handler """
    log_event(event)
    instance_id = get_instance_id(event)
    bucket = find_bucket()

    if resources_exist(instance_id, bucket) and is_a_garlc_instance(instance_id):
        artifact = find_newest_artifact(bucket)
        commands = ssm_commands(artifact)
        send_run_command(instance_id, commands)
        LOGGER.info('===SUCCESS===')
        return True
    else:
        return False
