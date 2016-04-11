"""
Unit Tests for trigger_run_command Lambda function
"""
from mock import patch, MagicMock
from lambda_bootstrap import find_bucket
from aws_lambda_sample_events import SampleEvent
from botocore.exceptions import ClientError
from lambda_bootstrap import is_a_garlc_instance
from lambda_bootstrap import find_newest_artifact
from lambda_bootstrap import get_instance_id
from lambda_bootstrap import resources_exist

@patch('boto3.client')
def test_find_bucket(mock_client):
    """
    Test the find_bucket function with valid event
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
    tests resources_exist function returns false when either arg is null
    """
    instance_id = "i-12345678"
    bucket = "buckette"
    assert resources_exist(instance_id, bucket) is True
