#!/bin/bash
# joshcb@amazon.com
# Generates an Ansible Inventory file from an EC2 Tag
# v1.1.0

# Set environment for ec2 tools
source ~/.bash_profile

# Get Region and Instance ID
region=`curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}'`
instance_id=`/opt/aws/bin/ec2-metadata -i | cut -d ' ' -f2`

# Query metadata for our instance id and fetch values of the Roles tag
tags="$(/opt/aws/bin/ec2-describe-tags --region $region --filter \"resource-type=instance\" \
  --filter \"resource-id=$instance_id\" --filter \"key=Roles\" | cut -f5)"

# Whitespace get outta here we don't need you
tags_no_whitespace="$(echo -e "${tags}" | tr -d '[[:space:]]')"

# Wipe out existing file :fire:
printf '' > /tmp/inventory

# http://stackoverflow.com/questions/10586153/split-string-into-an-array-in-bash
IFS=', ' read -r -a array <<< "$tags_no_whitespace"

# Write out each role into an Ansible host group
for element in "${array[@]}"
do
    printf "[$element]\nlocalhost ansible_connection=local\n" >> /tmp/inventory
done
