"""
Unit Tests for trigger_run_command Lambda function
"""
from mock import patch, MagicMock
from botocore.exceptions import ClientError
from runcommand_helper import send_run_command
from runcommand_helper import invoke_lambda
from runcommand_helper import handle

@patch('boto3.client')
def test_send_run_command(mock_client):
    """
    Test the send_run_command function without errors
    """
    ssm = MagicMock()
    mock_client.return_value = ssm
    ssm.send_command.return_value = True
    assert send_run_command(['i-12345678'], ['blah']) is True

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

@patch('runcommand_helper.send_run_command')
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

def test_invoke_lambda_with_no_chunks_remaining():
    """
    Test invoke_lambda when there are no chunks remaining to process
    """
    assert invoke_lambda([], []) is True

@patch('boto3.client')
def test_invoke_lambda(mock_client):
    """
    Test invoke_lambda with valid input and no errors
    """
    client = MagicMock()
    mock_client.return_value = client
    client.invoke_async.return_value = {"Status": 202}
    assert invoke_lambda([["blah"]], ["blah"]) is True

@patch('boto3.client')
def test_invoke_lambda_with_bad_status_code(mock_client):
    """
    Test invoke_lambda when a bad status code is returned
    """
    client = MagicMock()
    mock_client.return_value = client
    client.invoke_async.return_value = {"Status": 400}
    assert invoke_lambda([["blah"]], ["blah"]) is False

@patch('runcommand_helper.invoke_lambda')
@patch('boto3.client')
def test_invoke_lambda_with_clienterror(mock_client, mock_invoke):
    """
    Test invoke_lambda with valid input and a ClientError
    """
    err_msg = {
        'Error': {
            'Code': 400,
            'Message': 'Boom!'
        }
    }
    mock_client.side_effect = ClientError(err_msg, 'blah')
    assert invoke_lambda([["blah"]], ["blah"]) is False

@patch('runcommand_helper.invoke_lambda')
@patch('runcommand_helper.send_run_command')
def test_handle(mock_ssm, mock_invoke):
    """
    Test the handle function with valid input and no errors
    """
    mock_ssm.return_value = True
    mock_invoke.return_value = True
    event = {
        "ChunkedInstanceIds": [[1,2], [3,4]],
        "Commands": ["blah"]
    }
    assert handle(event, 'blah') is True

def test_handle_with_typeerror():
    """
    Test the handle function with invalid event and TypeError
    """
    event = ""
    assert handle(event, 'blah') is False

def test_handle_with_keyerror():
    """
    Test the handle function with invalid event and KeyError
    """
    event = {
        "ChunkedInstanceIds": [[1,2], [3,4]],
        "Blah": ["blah"]
    }
    assert handle(event, 'blah') is False
