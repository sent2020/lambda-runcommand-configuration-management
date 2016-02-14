# GARLC
Git  
Ansible  
Run Command  
Lambda  
CodePipeline  

# What witchcraft is this?
This is SSH-less, continuous configuration management (boom new buzzword).  This is the future.

1. Create/Update an Ansible playbook
* git push
* CodePipeline picks up your changes and invokes a Lambda function
* The Lambda function tells Run Command to trigger your instances to self update
* ???
* Profit

# Crude Setup Instructions for a Demo
1. Fork this repo
* Install [Apex](https://github.com/apex/apex)
* Create an IAM Role named "lambda_garlc".  It should have the following policies:
  * AWSLambdaBasicExecutionRole (AWS supplied)
  * AmazonEC2ReadOnlyAccess (AWS supplied)
  * A policy allowing all Actions for CodePipeline (reference iam_policies/Role_lambda_garlc/all_codepipeline_actions.json in this repo)
  * A policy allowing all Actions for SSM (reference iam_policies/Role_lambda_garlc/lambda_ssm.json in this repo)
* Create an EC2 Instance Profile with the following policies:
  * AmazonEC2RoleforSSM
  * AmazonEC2ReadOnlyAccess
* Spin up two Amazon Linux instances with the [Run Command agent](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/remote-commands-prereq.html) on them using the Instance Profile you create previously.
* Tag one instance with "Roles" and a value of "webserver,appserver"
* Tag one instance with "Roles" and a value of "dbserver"
* From the repo parent directory run `apex deploy -C lambda/`
* Create a CodePipeline with two stages:
  * Source stage should fetch from your fork of this repo on the master branch
  * Second stage should be an Invoke on the "garlic_trigger_run_command" Lambda function
  * NOTE:  If using the AWS Console to create your Pipeline you will be forced to add a "Beta" stage which you can later delete and replace with the Invoke stage.  Just add whatever to get through the wizard.
* Update something in the repository (e.g. add something to the Ansible playbook) and then commit to the master branch and watch your changes flow and your instances update automagically :fire:

# Notes
* Run Command has [no cost](https://aws.amazon.com/ec2/run-command/)
* Instances need a tag of "has_ssm_agent" with a value of "true" or "True"
* Instances must have a "Roles" tag (case sensitive) with a list of role names as a comma separated list
  * These roles correspond to Ansible roles in the playbook
