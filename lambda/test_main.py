"""
Unit Tests for trigger_run_command Lambda function
"""
import pytest
from botocore.exceptions import ClientError
from mock import MagicMock, patch
from main import find_artifact
from main import ssm_commands
from main import codepipeline_success
from main import codepipeline_failure
from main import find_instances
from main import send_run_command
from main import handle
from main import execute_runcommand
from freezegun import freeze_time

def test_find_artifact():
    """
    Test the find_artifact function with valid event
    """
    event = {
        'CodePipeline.job': {
            'data': {
                'inputArtifacts': [{
                    'location': {
                        's3Location': {
                            'objectKey': 'test/key',
                            'bucketName': 'bucket'
                        }
                    }
                }]
            }
        }
    }
    assert find_artifact(event) == 's3://bucket/test/key'

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

@patch('boto3.resource')
def test_find_instances(mock_client):
    """
    Test the find_instances function without errors
    """
    ec2 = MagicMock()
    mock_client.return_value = ec2
    instances = ['abcdef-12345']
    ec2.instances.return_value.all.return_value.filter.return_value = instances
    assert find_instances() == 'balls'

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

@patch('boto3.client')
def test_send_run_command(mock_client):
    """
    Test the send_run_command function without errors
    """
    ssm = MagicMock()
    mock_client.return_value = ssm
    ssm.send_command.return_value = True
    assert send_run_command(['abcdef-12345'], ['blah'])

@patch('boto3.client')
def test_send_run_command_invalid(mock_client):
    """
    Test the send_run_command function when a boto exception occurs
    """
    ssm = MagicMock()
    mock_client.return_value = ssm
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    ssm.send_command.side_effect = ClientError(err_msg, 'Test')
    assert send_run_command(['abcdef-12345'], ['blah']) is False

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
    event = {
        'CodePipeline.job': {
            'id': 'abc123'
        }
    }
    assert handle(event, 'Test')

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
    event = {
        'CodePipeline.job': {
            'id': 'abc123'
        }
    }
    assert handle(event, 'Test') is False

@patch('main.codepipeline_success')
@patch('main.send_run_command')
def test_execute_runcommand(mock_run_command, mock_success):
    """
    Test the execute_runcommand function with valid input
    """
    mock_run_command.return_value = True
    mock_success.return_value = True
    chunked_instance_ids = ['abcdef-12345']
    commands = ['blah']
    job_id = 1
    assert execute_runcommand(chunked_instance_ids, commands, job_id)

@patch('main.codepipeline_failure')
@patch('main.send_run_command')
def test_execute_runcommand_failed(mock_run_command, mock_failure):
    """
    Test the execute_runcommand function with valid input
    """
    mock_run_command.return_value = False
    mock_failure.return_value = True
    chunked_instance_ids = ['abcdef-12345']
    commands = ['blah']
    job_id = 1
    assert execute_runcommand(chunked_instance_ids, commands, job_id) is False
