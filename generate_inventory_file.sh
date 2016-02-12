#!/bin/bash
# joshcb@amazon.com
# Generates an Ansible Inventory file from an EC2 Tag
# v1.0.0

# Query metadata for our instance id and fetch values of the Roles tag
tags=`ec2-describe-tags --filter "resource-type=instance" \
  --filter "resource-id=$(ec2-metadata -i | cut -d ' ' -f2)" \
  --filter "key=Roles" | cut -f5`
# Whitespace get outta here we don't need you
tags_no_whitespace="$(echo -e "${tags}" | tr -d '[[:space:]]')"

# Wipe out existing file :fire:
printf '' > /tmp/inventory

# Sweet mother of... what is this witchcraft?!?!
# I literally do not understand how this works
# http://stackoverflow.com/questions/10586153/split-string-into-an-array-in-bash
# http://timmurphy.org/2012/03/09/convert-a-delimited-string-into-an-array-in-bash/
# This undoubtedly invokes some kind of unholy wrath :astonished:
IFS=', ' read -r -a array <<< "$tags_no_whitespace"

# Write out each role into an Ansible host group
for element in "${array[@]}"
do
    printf "[$element]\nlocalhost ansible_connection=local\n" >> /tmp/inventory
done
