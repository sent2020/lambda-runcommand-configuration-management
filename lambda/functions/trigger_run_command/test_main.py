"""
Unit Tests for trigger_run_command Lambda function
"""
import pytest
import botocore
from mock import MagicMock, Mock
from main import log_event_and_context
from main import find_artifact
from main import ssm_commands
from main import codepipeline_success
from main import codepipeline_failure
from main import find_instances
from main import send_run_command
from main import handle
from freezegun import freeze_time

def test_log_event_and_context():
    """
    Test the log_event_and_context function
    """
    assert log_event_and_context

def test_find_artifact():
    """
    Test the log_event_and_context function with valid event
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
    Test the log_event_and_context function with invalid event
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

def test_codepipeline_success(monkeypatch):
    """
    Test the codepipeline_success function with valid data
    """
    boto3 = MagicMock()
    monkeypatch.setattr('boto3.client', MagicMock(return_value=boto3))
    monkeypatch.setattr('boto3.client.put_job_success_result', MagicMock(return_value=True))
    assert codepipeline_success(1) == True

def test_codepipeline_success_invalid(monkeypatch):
    """
    Test the codepipeline_success function with invalid data
    """
    boto3 = MagicMock()
    monkeypatch.setattr('boto3.client', MagicMock(return_value=boto3))
    monkeypatch.setattr('boto3.client.put_job_success_result', Mock(side_effect=botocore.exceptions.ClientError))
    with pytest.raises(botocore.exceptions.ClientError):
        assert codepipeline_success(1)

def test_codepipeline_failure(monkeypatch):
    """
    Test the codepipeline_failure function with valid data
    """
    boto3 = MagicMock()
    monkeypatch.setattr('boto3.client', MagicMock(return_value=boto3))
    monkeypatch.setattr('boto3.client.put_job_failure_result', MagicMock(return_value=True))
    assert codepipeline_failure(1, 'blah') == True

def test_codepipeline_failure_invalid(monkeypatch):
    """
    Test the codepipeline_failure function with invalid data
    """
    boto3 = MagicMock()
    monkeypatch.setattr('boto3.client', MagicMock(return_value=boto3))
    monkeypatch.setattr('boto3.client.put_job_success_result', Mock(side_effect=botocore.exceptions.ClientError))
    with pytest.raises(botocore.exceptions.ClientError):
        assert codepipeline_failure(1, 'blah')

def test_find_instances(monkeypatch):
    """
    Test the find_instances function without errors
    """
    boto3 = MagicMock()
    instances = {
        'Reservations': [{
            'Instances': [{
                'InstanceId': 'abcdef-12345'
            }]
        }]
    }
    monkeypatch.setattr('boto3.client', MagicMock(return_value=boto3))
    monkeypatch.setattr('boto3.client.describe_instances', MagicMock(return_value=instances))
    assert find_instances() == 'abcdef-12345'
