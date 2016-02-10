# GARLC
GitHub  
Ansible  
Run Command  
Lambda  
CodePipeline  

# TODO
* Automate IAM role creation for Lambda function
* Automate creation of CodePipeline
* Instructions and packaging around Run Command
* Setup S3 Bucket for Run Command history
* Target a set of instances
* Fix git cloning, should probably fetch
* Bootstrapping of new instances that will be consumers
  * Getting SSM agent on there
  * Setting up Ansible
* Reporting back on success/failure
  * CloudWatch Dashboard?
* Lambda function needs error handling and status reporting

# Notes
* Run Command has [no cost](https://aws.amazon.com/ec2/run-command/)
* CodePipeline is max 20 pipelines per account (soft?)
  * Leaning towards one pipeline, one repo to rule them all
    * Ansible roles and let the instance query metadata to get its own tags (tags == roles)
* Currently, instances need a tag of "has_ssm_agent" with a value of "true" or "True"
