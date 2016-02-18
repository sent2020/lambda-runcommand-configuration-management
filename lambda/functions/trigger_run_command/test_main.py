"""
Unit Tests for trigger_run_command Lambda function
"""
from main import ssm_commands
from freezegun import freeze_time

@freeze_time('2016-01-01')

def test_ssm_commands():
    artifact = 'bucket/test/key'
    commands = [
    'aws configure set s3.signature_version s3v4',
    'aws s3 cp bucket/test/key /tmp/20160101000000.zip --quiet',
    'unzip -qq /tmp/20160101000000.zip -d /tmp/20160101000000',
    'bash /tmp/20160101000000/generate_inventory_file.sh',
    'ansible-playbook -i "/tmp/inventory" /tmp/20160101000000/ansible/playbook.yml'
    ]
    assert ssm_commands(artifact) == commands
