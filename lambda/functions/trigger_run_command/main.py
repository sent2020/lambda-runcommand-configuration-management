"""
Triggers Run Command on all instances with tag has_ssm_agent set to true,
refreshes the git repository or clones it if it doesn't exist, and finally
run Ansible locally on the instance to configure itself.
joshcb@amazon.com
v1.2.0
"""
from __future__ import print_function
import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

COMMANDS = [
    'if cd /tmp/garlc; then git pull; else git clone ' \
    'https://github.com/irlrobot/garlc.git /tmp/garlc; fi',
    'ansible-playbook -i "localhost," -c local /tmp/garlc/ansible/playbook.yml'
]

def log_event_and_context(event, context):
    """Logs event information for debugging"""
    LOGGER.info("====================================================")
    LOGGER.info(context)
    LOGGER.info("====================================================")
    LOGGER.info(event)
    LOGGER.info("====================================================")

def codepipeline_sucess(codepipeline, job_id):
    """
    Puts CodePipeline Sucess Result
    """
    codepipeline.put_job_success_result(jobId=job_id)

def codepipeline_failure(codepipeline, job_id, message):
    """
    Puts CodePipeline Failure Result
    """
    codepipeline.put_job_failure_result(
        jobId=job_id,
        failureDetails={'type': 'JobFailed', 'message': message}
    )

def handle(event, context):
    """
    Lambda main handler
    """
    # TODO
    # Better error handling, this is awful!
    try:
        log_event_and_context(event, context)
        ssm = boto3.client('ssm')
        ec2 = boto3.client('ec2')
        codepipeline = boto3.client('codepipeline')

        filters = [{
            'Name': 'tag:has_ssm_agent',
            'Values': ['true', 'True']
        }]
        instances = ec2.describe_instances(Filters=filters)
        job_id = event['CodePipeline.job']['id']
        instance_ids = []

        for instance in instances['Reservations']:
            instance_ids.append(instance['Instances'][0]['InstanceId'])

        ssm.send_command(
            InstanceIds=instance_ids,
            DocumentName='AWS-RunShellScript',
            TimeoutSeconds=60,
            Parameters={
                'commands': COMMANDS,
                'executionTimeout': ['120']
            }
        )

        codepipeline_sucess(codepipeline, job_id)
    except Exception as err:
        codepipeline_failure(codepipeline, job_id, err)
