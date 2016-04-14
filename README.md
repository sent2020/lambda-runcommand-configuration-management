# What's That Smell?
Project GARLC is made up of:
* Git – for configuration storage and version control.  GitHub is used for the project currently but you could also use CodeCommit.
* Ansible – for configuration management.  Chef, Puppet, or Salt using their respective “masterless” or “solo” modes could also be used.
* Amazon EC2 Run Command – for executing Ansible without requiring SSH access to the instances.
* AWS Lambda – for executing logic and invoking RunCommand.
* AWS CodePipeline – for receiving changes from git and triggering Lambda.

The general idea is that configuration management is now done in the same way we do continuous delivery of applications today.  What makes GARLC really exciting though is that there are no central control/orchestration servers to maintain and we no longer need SSH access to the instances to configure them.  There are two modes to Project GARLC:  continuous and bootstrap.

**Blog post for detailed introduction coming soon**

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

# Theme Song
No ssh here,  
sudo git me a beer,   
while I Ansible all the things.

Swaggin with RunCommand,  
Lambda don’t move a hand,   
flowin through the CodePipeline.  

Smells like GARLC, GARLC, GARLC…  
Smells like GARLC, GARLC, GARLC…  
Smells like GARLC, GARLC, GARLC…  
