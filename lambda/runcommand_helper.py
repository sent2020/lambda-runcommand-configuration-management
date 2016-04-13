"""
Triggers Run Command on all instances specified.  This helper function is used
in order to scale out GARLC.  The function is recursively called in batches
so AWS Lambda timeout's are avoided.  RunCommand throttling is handled as well.
joshcb@amazon.com
v1.0.0
"""
from __future__ import print_function
import json
import logging
from botocore.exceptions import ClientError
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def send_run_command(instance_ids, commands):
    """
    Tries to queue a RunCommand job.  If a ThrottlingException is encountered
    recursively calls itself until success.
    """
    try:
        ssm = boto3.client('ssm')
    except ClientError as err:
        LOGGER.error("Run Command Failed!\n%s", str(err))
        return False

    try:
        ssm.send_command(
            InstanceIds=instance_ids,
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['600'] # Seconds all commands have to complete in
            }
        )
        LOGGER.info('============RunCommand sent successfully')
        return True
    except ClientError as err:
        if 'ThrottlingException' in str(err):
            LOGGER.info("RunCommand throttled, automatically retrying...")
            send_run_command(instance_ids, commands)
        else:
            LOGGER.error("Run Command Failed!\n%s", str(err))
            return False

def invoke_lambda(chunks, commands):
    """
    Hands off the remaining work to another Lambda function.  This is done
    to avoid hitting AWS Lambda timeouts with a single Lambda function.
    """
    if len(chunks) == 0:
        LOGGER.info('No more chunks of instances to process')
        return True
    else:
        try:
            client = boto3.client('lambda')
        except ClientError as err:
            # Log the error and keep trying until we timeout
            LOGGER.error("Failed to created a Lambda client!\n%s", err)
            invoke_lambda(chunks, commands)

        event = {
            "ChunkedInstanceIds": chunks,
            "Commands": commands
        }
        response = client.invoke_async(
            FunctionName='garlc_runcommand_helper',
            InvokeArgs=json.dumps(event)
        )

        if response['Status'] is 202:
            LOGGER.info('Invoked the next Lambda function to continue...')
            return True
        else:
            LOGGER.error(response)
            return False

def handle(event, _context):
    """
    Lambda main handler
    """
    LOGGER.info(event)
    try:
        chunked_instance_ids = event['ChunkedInstanceIds']
        LOGGER.debug('==========Chunks remaining:')
        LOGGER.debug(len(chunked_instance_ids))
        commands = event['Commands']
    except (TypeError, KeyError) as err:
        LOGGER.error("Could not parse event!\n%s", err)
        return False

    # We work on one chunk at a time until there are no more chunks left.
    # Each chunk is handled by a new AWS Lambda function.
    instance_ids = chunked_instance_ids.pop(0)
    LOGGER.debug('==========Instances in this chunk:')
    LOGGER.debug(instance_ids)
    send_run_command(instance_ids, commands)
    invoke_lambda(chunked_instance_ids, commands)
    return True
