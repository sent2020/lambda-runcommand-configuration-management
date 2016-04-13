"""
Unit Tests for trigger_run_command Lambda function
"""
from mock import patch, MagicMock
from aws_lambda_sample_events import SampleEvent
from botocore.exceptions import ClientError
from bootstrap import find_bucket
from bootstrap import is_a_garlc_instance
from bootstrap import find_newest_artifact
from bootstrap import get_instance_id
from bootstrap import resources_exist
from bootstrap import send_run_command
from bootstrap import handle

@patch('boto3.client')
def test_find_bucket(mock_client):
    """
    Test the find_bucket function with valid input
    """
    pipeline_object = {
        "pipeline": {
            "artifactStore": {
                "location": "blah"
            }
        }
    }
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    codepipeline.get_pipeline.return_value = pipeline_object
    assert find_bucket() == 'blah'

@patch('boto3.client')
def test_find_bucket_with_typeerror(mock_client):
    """
    Test the find_bucket functin with a TypeError
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    codepipeline.get_pipeline.return_value = {'blah'}
    assert find_bucket() == False

@patch('boto3.client')
def test_find_bucket_with_keyerror(mock_client):
    """
    Test the find_bucket functin with a KeyError
    """
    codepipeline = MagicMock()
    mock_client.return_value = codepipeline
    codepipeline.get_pipeline.return_value = {"blah": "blah"}
    assert find_bucket() == False

@patch('boto3.client')
def test_find_bucket_with_clienterror(mock_client):
    """
    Test the find_bucket function with a KeyError
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'blah')
    assert find_bucket() is False

@patch('boto3.client')
def test_is_a_garlc_instance(mock_client):
    """
    Test is_a_garlc_instance returns true when EC2 API Call
    returns a string
    """
    ec2 = MagicMock()
    mock_client.return_value = ec2
    ec2.describe_instances.return_value = "instance"
    assert is_a_garlc_instance("instance") is True

@patch('boto3.client')
def test_is_a_garlc_instance_except_when_its_not(mock_client):
    """
    Test is_a_garlc_instance returns false when it's missing the tag
    """
    ec2 = MagicMock()
    mock_client.return_value = ec2
    ec2.describe_instances.return_value = ""
    assert is_a_garlc_instance("instance") is False

@patch('boto3.client')
def test_is_a_garlc_instance_with_clienterror(mock_client):
    """
    Test is_a_garlc_instance with ClientError
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Sad Code'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'sad response')
    assert is_a_garlc_instance('foo') is False

@patch('boto3.client')
def test_find_newest_artifact(mock_client):
    """
    test find_newest_artifact returns a properly formatted string
    """
    bucket_objects = {
        "Contents": [
            {
                "Key": "blah",
                "LastModified": "datetime.datetime(2016, 3, 18, 19, 20, 29, tzinfo=tzutc())"
            }
        ]
    }
    aws_s3 = MagicMock()
    mock_client.return_value = aws_s3
    aws_s3.list_objects.return_value = bucket_objects
    assert find_newest_artifact('blah') == 's3://blah/blah'

@patch('boto3.client')
def test_find_newest_artifact_with_keyerror(mock_client):
    """
    test find_newest_artifact returns false with a KeyError
    """
    bucket_objects = {
        "Contents": [
            {
                "LastModified": "datetime.datetime(2016, 3, 18, 19, 20, 29, tzinfo=tzutc())"
            }
        ]
    }
    aws_s3 = MagicMock()
    mock_client.return_value = aws_s3
    aws_s3.list_objects.return_value = bucket_objects
    assert find_newest_artifact('blah') is False

@patch('boto3.client')
def test_find_newest_artifact_with_clienterror(mock_client):
    """
    test find_newest_artifact returns false with a ClientError
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'blah')
    assert find_newest_artifact('blah') is False

@patch('boto3.client')
def test_get_instance_id(mock_event):
    """
    test get instance id returns instance id string
    """
    mock_event = {
        'detail': {
            'instance-id': 'i-12345678'
        }
    }
    assert get_instance_id(mock_event) == mock_event['detail']['instance-id']

@patch('boto3.client')
def test_resources_exist(mock_event):
    """
    tests resources_exist function
    """
    instance_id = "i-12345678"
    bucket = "buckette"
    assert resources_exist(instance_id, bucket) is True

@patch('boto3.client')
def test_resources_exist_when_missing_instance_id(mock_event):
    """
    tests resources_exist function returns false when instance_id is blank
    """
    instance_id = ''
    bucket = 'buckette'
    assert resources_exist(instance_id, bucket) is False

@patch('boto3.client')
def test_resources_exist_when_missing_bucket(mock_event):
    """
    tests resources_exist function returns false when bucket is None
    """
    instance_id = "i-12345678"
    bucket = None
    assert resources_exist(instance_id, bucket) is False

@patch('boto3.client')
def test_send_run_command(mock_client):
    """
    Test the send_run_command function without errors
    """
    ssm = MagicMock()
    mock_client.return_value = ssm
    ssm.send_command.return_value = True
    assert send_run_command(['i-12345678'], ['blah'])

@patch('boto3.client')
def test_send_run_command_with_clienterror(mock_client):
    """
    Test the send_run_command function with ClientError
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'blah')
    assert send_run_command('blah', 'blah') is False

@patch('boto3.client')
def test_send_run_command_with_clienterror_during_send_command(mock_client):
    """
    Test the send_run_command function with a ClientError from send_command
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    ssm = MagicMock()
    mock_client.return_value = ssm
    ssm.send_command.side_effect = ClientError(err_msg, 'blah')
    assert send_run_command('blah', 'blah') is False

@patch('bootstrap.send_run_command')
@patch('boto3.client')
def test_send_run_command_with_throttlingexception(mock_client, mock_run_command):
    """
    Test the send_run_command function with a ThrottlingException
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'ThrottlingException'
        }
    }
    ssm = MagicMock()
    mock_client.return_value = ssm
    ssm.send_command.side_effect = ClientError(err_msg, 'blah')
    assert send_run_command('blah', 'blah') is not False

@patch('bootstrap.send_run_command')
@patch('bootstrap.find_newest_artifact')
@patch('bootstrap.is_a_garlc_instance')
@patch('bootstrap.find_bucket')
def test_handle(mock_find_bucket, mock_is_instance, mock_artifact, mock_ssm):
    """
    Test the handle function with valid input
    """
    event = SampleEvent('cloudwatch_events')
    mock_find_bucket.return_value = 'buckette'
    mock_is_instance.return_value = True
    mock_artifact.return_value = 's3://blah/blah.zip'
    mock_ssm.return_value = True
    assert handle(event.event, 'blah') is True

@patch('bootstrap.find_bucket')
def test_handle_with_invalid_bucket(mock_find_bucket):
    """
    Test the handle function with invalid bucket
    """
    event = SampleEvent('cloudwatch_events')
    mock_find_bucket.return_value = ''
    assert handle(event.event, 'blah') is False

@patch('bootstrap.find_bucket')
def test_handle_with_invalid_event(mock_find_bucket):
    """
    Test the handle function with invalid event
    """
    event = 'blah'
    mock_find_bucket.return_value = 'buckette'
    assert handle(event, 'blah') is False
