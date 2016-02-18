"""
Unit Tests for trigger_run_command Lambda function
"""
import pytest
from main import log_event_and_context
from main import find_artifact
from main import ssm_commands
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
