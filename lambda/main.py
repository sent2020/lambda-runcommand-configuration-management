"""
Triggers Run Command on all instances with tag has_ssm_agent set to true.
Fetches artifact from S3 via CodePipeline, extracts the contents, and finally
run Ansible locally on the instance to configure itself.
joshcb@amazon.com
v1.1.0
"""
from __future__ import print_function
import datetime
import logging
from botocore.exceptions import ClientError
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def log_event_and_context(event, context):
    """Logs event information for debugging"""
    LOGGER.info("====================================================")
    LOGGER.info(context)
    LOGGER.info("====================================================")
    LOGGER.info(event)
    LOGGER.info("====================================================")

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
        ec2 = boto3.client('ec2')
        # TODO: add pagination to the below call, MaxResults max is 1000
        instances = ec2.describe_instances(Filters=filters, MaxResults=1000)
    except ClientError as err:
        LOGGER.error("Failed to DescribeInstances with EC2!\n%s", err)

    try:
        for instance in instances['Reservations']:
            instance_ids.append(instance['Instances'][0]['InstanceId'])
    except KeyError as err:
        LOGGER.error("Unable to parse returned instances dict in " \
            "`find_instances` function!\n%s", err)

    LOGGER.info("Instance IDs: " + str(instance_ids))
    return instance_ids

def break_instance_ids_into_chunks(instance_ids):
    """
    Returns successive chunks of 50 from instance_ids
    """
    size = 50
    return [instance_ids[i:i + size] for i in range(0, len(instance_ids), size)]

def execute_runcommand(chunked_instance_ids, commands, job_id):
    """
    Execute RunCommand for each chunk of instances
    """
    success = True
    for chunk in chunked_instance_ids:
        if send_run_command(chunk, commands) is False:
            success = False # continue iterating but make sure we fail the pipeline

    if success:
        codepipeline_success(job_id)
        return True
    else:
        codepipeline_failure(job_id, 'Not all RunCommand calls completed, see log.')
        return False

def send_run_command(instance_ids, commands):
    """
    Sends the Run Command API Call
    """
    try:
        ssm = boto3.client('ssm')
        ssm.send_command(
            InstanceIds=instance_ids,
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

def handle(event, context):
    """
    Lambda main handler
    """
    log_event_and_context(event, context)
    try:
        job_id = event['CodePipeline.job']['id']
    except KeyError as err:
        # TODO
        # Better handle manual lambda invocations
        # This will cause a ParamValidationError
        job_id = 1
        LOGGER.error("Could not retrieve CodePipeline Job ID!\n%s", err)

    instance_ids = find_instances()
    commands = ssm_commands(find_artifact(event))
    if len(instance_ids) != 0:
        chunked_instance_ids = break_instance_ids_into_chunks(instance_ids)
        execute_runcommand(chunked_instance_ids, commands, job_id)
        return True
    else:
        codepipeline_failure(job_id, 'No Instance IDs Provided!')
        return False
