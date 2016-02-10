# GARLC
GitHub  
Ansible  
Run Command  
Lambda  
CodePipeline  

# TODO
* Automate IAM role creation for Lambda function
* Dynamically target instances for Run Command
  * Tags?
* Automate creation of CodePipeline
* Instructions and packaging around Run Command
* Setup S3 Bucket for Run Command history
* Target a set of instances
* Fix git cloning, should probably fetch
* Bootstrapping of new instances that will be consumers
  * Getting SSM agent on there
  * Setting up Ansible

# Notes
* Run Command has [no cost](https://aws.amazon.com/ec2/run-command/)
* CodePipeline is max 20 pipelines per account (soft?)
