"""
Validates HTTP Status of Environment
joshcb@amazon.com
v1.0.1
"""
from __future__ import print_function
import logging
from urllib2 import urlopen, URLError, HTTPError
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

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
    codepipeline = boto3.client('codepipeline')
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    url = job_data['actionConfiguration']['configuration']['UserParameters']
    try:
        request = urlopen(url)
        response_code = request.getcode()
    except HTTPError as err:
        LOGGER.error("Request failed: %d %s", err.code, err.reason)
        codepipeline_failure(codepipeline, job_id, err.reason)
    except URLError as err:
        LOGGER.error("Server connection failed: %s", err.reason)
        codepipeline_failure(codepipeline, job_id, err.reason)

    if response_code == 200:
        codepipeline_sucess(codepipeline, job_id)
    else:
        codepipeline_failure(codepipeline, job_data, ("Returned %d", response_code))
