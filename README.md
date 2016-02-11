# GARLC
Git  
Ansible  
Run Command  
Lambda  
CodePipeline  

# Notes
* Run Command has [no cost](https://aws.amazon.com/ec2/run-command/)
* CodePipeline is max 20 pipelines per account (soft?)
  * Leaning towards one pipeline, one repo to rule them all
    * Ansible roles and let the instance query metadata to get its own tags (tags == roles)
* Currently, instances need a tag of "has_ssm_agent" with a value of "true" or "True"
