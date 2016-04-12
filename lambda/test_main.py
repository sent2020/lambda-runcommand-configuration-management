"""
Unit Tests for trigger_run_command Lambda function
"""
import pytest
import boto3
from botocore.exceptions import ClientError
from mock import MagicMock, patch
from main import find_artifact
from main import ssm_commands
from main import codepipeline_success
from main import codepipeline_failure
from main import find_instances
from main import handle
from main import execute_runcommand
from main import find_instance_ids
from freezegun import freeze_time
from aws_lambda_sample_events import SampleEvent

def test_find_artifact():
    """
    Test the find_artifact function with valid event
    """
    codepipeline = SampleEvent('codepipeline')
    assert find_artifact(codepipeline.event) == \
        's3://codepipeline-us-east-1-123456789000/pipeline/MyApp/random.zip'

def test_find_artifact_invalid():
    """
    Test the find_artifact function with invalid event
    """
    event = {}
    with pytest.raises(KeyError):
        assert find_artifact(event) == 'blah'

@freeze_time('2016-01-01')
def test_ssm_commands():
    """
    Test the ssm_commands function
    """
    artifact = 'bucket/test/key'
    commands = [
        'export AWS_DEFAULT_REGION=`curl -s http://169.254.169.254/' \
        "latest/dynamic/instance-identity/document | grep region | awk -F\\\" '{print $4}'`",
        'aws configure set s3.signature_version s3v4',
        'aws s3 cp bucket/test/key /tmp/20160101000000.zip --quiet',
        'unzip -qq /tmp/20160101000000.zip -d /tmp/20160101000000',
        'bash /tmp/20160101000000/generate_inventory_file.sh',
        'ansible-playbook -i "/tmp/inventory" /tmp/20160101000000/ansible/playbook.yml'
    ]
    assert ssm_commands(artifact) == commands

@patch('boto3.client')
def test_codepipeline_success(mock_client):
    """
    Test the codepipeline_success function with valid data
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    codepipeline.put_job_success_result.return_value = True
    assert codepipeline_success(1)

@patch('boto3.client')
def test_codepipeline_success_with_exception(mock_client):
    """
    Test the codepipeline_success function when a boto exception occurs
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    codepipeline.put_job_success_result.side_effect = ClientError(err_msg, 'Test')
    assert codepipeline_success(1) is False

@patch('boto3.client')
def test_codepipeline_failure(mock_client):
    """
    Test the codepipeline_failure function with valid data
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    codepipeline.put_job_failure_result.return_value = True
    assert codepipeline_failure(1, 'blah')

@patch('boto3.client')
def test_codepipeline_failure_with_exception(mock_client):
    """
    Test the codepipeline_failure function when a boto exception occurs
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    codepipeline.put_job_failure_result.side_effect = ClientError(err_msg, 'Test')
    assert codepipeline_failure(1, 'blah') is False

@patch('main.find_instance_ids')
def test_find_instances(mock_instances):
    """
    Test the find_instances function without errors
    """
    instances = ['abcdef-12345']
    mock_instances.return_value = instances
    assert find_instances() == instances

@patch('boto3.resource')
def test_find_instances_boto_error(mock_client):
    """
    Test the find_instances function when a boto exception occurs
    """
    ec2 = MagicMock()
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.return_value = ec2
    ec2.instances.side_effect = ClientError(err_msg, 'Test')
    assert find_instances() == []

@patch('boto3.resources.collection.ResourceCollection.filter')
def test_find_instance_ids(mock_resource):
    """
    Test the find_instance_ids function
    """
    instance_id = 'abcdef-12345'
    instance = [MagicMock(id=instance_id)]
    boto3.setup_default_session(region_name='us-east-1')
    mock_resource.return_value = instance
    assert find_instance_ids('blah') == [instance_id]

@patch('main.codepipeline_success')
@patch('main.execute_runcommand')
@patch('main.find_artifact')
@patch('main.ssm_commands')
@patch('main.find_instances')
def test_handle(mock_instances, mock_commands, mock_artifact, mock_run_command,
                mock_success):
    """
    Test the handle function with valid input and instances
    """
    mock_instances.return_value = ['abcdef-12345']
    mock_commands.return_value = True
    mock_artifact.return_value = True
    mock_run_command.return_value = True
    mock_success.return_value = True
    codepipeline = SampleEvent('codepipeline')
    assert handle(codepipeline.event, 'Test')

@patch('main.codepipeline_failure')
@patch('main.find_artifact')
@patch('main.ssm_commands')
@patch('main.find_instances')
def test_handle_no_instances(mock_instances, mock_commands, mock_artifact,
                             mock_failure):
    """
    Test the handle function with valid input and no instances
    """
    mock_instances.return_value = []
    mock_commands.return_value = True
    mock_artifact.return_value = True
    mock_failure.return_value = True
    codepipeline = SampleEvent('codepipeline')
    assert handle(codepipeline.event, 'Test') is False

@patch('main.codepipeline_success')
@patch('boto3.client')
def test_execute_runcommand(mock_client, mock_success):
    """
    Test the execute_runcommand function with valid input
    """
    client = MagicMock()
    mock_client.return_value = client
    client.invoke_async.return_value = {"Status": 202}
    mock_success.return_value = True
    chunked_instance_ids = ['abcdef-12345']
    commands = ['blah']
    job_id = 1
    assert execute_runcommand(chunked_instance_ids, commands, job_id) is True

@patch('boto3.client')
def test_execute_runcommand_with_clienterror(mock_client):
    """
    Test the execute_runcommand function with valid input
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'Test')
    chunked_instance_ids = ['abcdef-12345']
    commands = ['blah']
    job_id = 1
    assert execute_runcommand(chunked_instance_ids, commands, job_id) is False
