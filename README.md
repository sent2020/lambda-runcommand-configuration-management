# What's That Smell?
This demonstrates serverless, SSH-less, continuous configuration management.  Affectionately referred to as GARLC:

GitHub  
Ansible  
RunCommand  
Lambda  
CodePipeline

1. Create/Update Ansible playbook(s)
* `git push` the playbook(s) into GitHub
* CodePipeline picks up your changes
* Lambda tells RunCommand to trigger your instances to self configure using Ansible
* ???
* Profit

# Setup Instructions for a Demo
**WARNING:  Using this code may cost you money.  Please be sure you understand your current usage and the costs associated with this reference code before launching in your AWS account.**
1. Fork this repo.
* Install [Terraform](https://www.terraform.io/downloads.html) to help setup the infrastructure required for GARLC.
* Manually create a [CodePipeline using the AWS Console](http://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-create-pipelines.html) with a single stage for now:
  * Source stage should fetch from your fork of this repo on the master branch.
    * Output should be "MyApp".
  * NOTE:  When using the AWS Console to create your Pipeline you will be forced to add a "Beta" stage which you can later delete and replace with the Invoke stage.  Just add whatever to get through the wizard.
* From the parent directory of your fork run the below to setup the infrastructure.  This will create IAM Roles, the Lambda function, and a couple Auto-Scaling Groups in us-west-2:
  1. `terraform get terraform`
  * `terraform plan terraform`
  * `terraform apply terraform`
* Go back to CodePipeline and add a second stage for an "Invoke" action on the "garlic" Lambda function created with Terraform in the previous step.
    * Input should be "MyApp".
* Update something in the repository (e.g. add something to an Ansible playbook) and then commit to the master branch and watch your changes flow and your instances update automagically :fire:.

# Notes
* Instances need a tag of "has_ssm_agent" with a value of "true" or "True".
* Instances must have an "Ansible_Roles" tag (case sensitive) with a list of role names as a comma separated list.
  * These roles should correspond to Ansible roles in the playbook to be useful.
