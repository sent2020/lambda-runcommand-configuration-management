"""
Triggers RunCommand on all instances with tag has_ssm_agent set to true.
Fetches artifact from S3 via CodePipeline, extracts the contents, and finally
runs Ansible locally on the instance to configure itself.  Uses
runcommand_helper.py to actually execute RunCommand.
joshcb@amazon.com
v1.1.0
"""
from __future__ import print_function
import json
import datetime
import logging
from botocore.exceptions import ClientError
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def find_artifact(event):
    """
    Returns the S3 Object that holds the artifact
    """
    try:
        object_key = event['CodePipeline.job']['data']['inputArtifacts'][0] \
            ['location']['s3Location']['objectKey']
        bucket = event['CodePipeline.job']['data']['inputArtifacts'][0] \
            ['location']['s3Location']['bucketName']
        return 's3://{0}/{1}'.format(bucket, object_key)
    except KeyError as err:
        raise KeyError("Couldn't get S3 object!\n%s", err)

def ssm_commands(artifact):
    """
    Builds commands to be sent to SSM (Run Command)
    """
    # TODO
    # Error handling in the command generation
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

def codepipeline_success(job_id):
    """
    Puts CodePipeline Success Result
    """
    try:
        codepipeline = boto3.client('codepipeline')
        codepipeline.put_job_success_result(jobId=job_id)
        LOGGER.info('===SUCCESS===')
        return True
    except ClientError as err:
        LOGGER.error("Failed to PutJobSuccessResult for CodePipeline!\n%s", err)
        return False

def codepipeline_failure(job_id, message):
    """
    Puts CodePipeline Failure Result
    """
    try:
        codepipeline = boto3.client('codepipeline')
        codepipeline.put_job_failure_result(
            jobId=job_id,
            failureDetails={'type': 'JobFailed', 'message': message}
        )
        LOGGER.info('===FAILURE===')
        return True
    except ClientError as err:
        LOGGER.error("Failed to PutJobFailureResult for CodePipeline!\n%s", err)
        return False

def find_instances():
    """
    Find Instances to invoke Run Command against
    """
    instance_ids = []
    filters = [
        {'Name': 'tag:has_ssm_agent', 'Values': ['true', 'True']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
    try:
        instance_ids = find_instance_ids(filters)
        print(instance_ids)
    except ClientError as err:
        LOGGER.error("Failed to DescribeInstances with EC2!\n%s", err)

    return instance_ids

def find_instance_ids(filters):
    """
    EC2 API calls to retrieve instances matched by the filter
    """
    ec2 = boto3.resource('ec2')
    return [i.id for i in ec2.instances.all().filter(Filters=filters)]

def break_instance_ids_into_chunks(instance_ids):
    """
    Returns successive chunks from instance_ids
    """
    size = 250
    chunks = []
    for i in range(0, len(instance_ids), size):
        chunks.append(instance_ids[i:i + size])
    return chunks

def execute_runcommand(chunked_instance_ids, commands, job_id):
    """
    Handoff RunCommand to the RunCommand Helper AWS Lambda function
    """
    try:
        client = boto3.client('lambda')
    except ClientError as err:
        LOGGER.error("Failed to created a Lambda client!\n%s", err)
        codepipeline_failure(job_id, err)
        return False

    event = {
        "ChunkedInstanceIds": chunked_instance_ids,
        "Commands": commands
    }
    response = client.invoke_async(
        FunctionName='garlc_runcommand_helper',
        InvokeArgs=json.dumps(event)
    )

    if response['Status'] is 202:
        codepipeline_success(job_id)
        return True
    else:
        codepipeline_failure(job_id, response)
        return False

def handle(event, _context):
    """
    Lambda main handler
    """
    LOGGER.info(event)
    try:
        job_id = event['CodePipeline.job']['id']
    except KeyError as err:
        LOGGER.error("Could not retrieve CodePipeline Job ID!\n%s", err)
        return False

    instance_ids = find_instances()
    commands = ssm_commands(find_artifact(event))
    if len(instance_ids) != 0:
        chunked_instance_ids = break_instance_ids_into_chunks(instance_ids)
        execute_runcommand(chunked_instance_ids, commands, job_id)
        return True
    else:
        codepipeline_failure(job_id, 'No Instance IDs Provided!')
        return False
