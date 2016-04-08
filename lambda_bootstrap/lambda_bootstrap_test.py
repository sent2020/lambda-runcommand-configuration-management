"""
Unit Tests for trigger_run_command Lambda function
"""
from mock import patch, MagicMock
from lambda_bootstrap import find_bucket
from aws_lambda_sample_events import SampleEvent
from botocore.exceptions import ClientError
from lambda_bootstrap import is_a_garlc_instance

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
    assert find_bucket() == False

@patch('boto3.client')
def test_is_a_garlc_instance(mock_client):
    """
    Test is_a_garlc_instance returns true when EC2 API Call
    returns a string
    """
    ec2 = MagicMock()
    mock_client.return_value = ec2
    ec2.describe_instances.return_value = "instance"
    assert is_a_garlc_instance("instance") == True
