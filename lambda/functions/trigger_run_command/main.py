"""
Initiates RunCommand
joshcb@amazon.com
v1.0.0
"""
from __future__ import print_function
import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def handle(event, context):
    """
    Lambda main handler
    """
    client = boto3.client('ssm')
    client.send_command(
        InstanceIds=[
            'i-5f0941ec',
            'i-011159b2'
        ],
        DocumentName='AWS-RunShellScript',
        TimeoutSeconds=60,
        Parameters={
            'commands': [
                'cd /tmp',
                'rm -rf garlc',
                'git clone https://github.com/irlrobot/garlc.git',
                'ansible-playbook -i "localhost," -c local garlc/ansible/playbook.yml'
            ],
            'executionTimeout': ['120']
        }
    )
