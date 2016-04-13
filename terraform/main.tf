provider "aws" {
  region = "${var.region}"
}

module "instance_profile" {
  source = "./iam"
}

module "lambda" {
  source = "./lambda"
}

module "vpc" {
  source = "./vpc"
  region = "${var.region}"
}

module "launch_configuration" {
  source = "./lc"
  iam_instance_profile = "${module.instance_profile.profile_name}"
  region = "${var.region}"
  key_name = "${var.key_name}"
  vpc_id = "${module.vpc.vpc_id}"
}

module "webserver_asg" {
  source = "./asg"
  lcid = "${module.launch_configuration.lcid}"
  max_size = 50
  min_size = 2
  desired_capacity = 2
  asg_name = "garlc_webservers"
  ansible_roles = "webserver,appserver"
  subnet1 = "${module.vpc.subnet1}"
  subnet2 = "${module.vpc.subnet2}"
}

module "database_asg" {
  source = "./asg"
  lcid = "${module.launch_configuration.lcid}"
  max_size = 5
  min_size = 1
  desired_capacity = 1
  asg_name = "garlc_databases"
  ansible_roles = "dbserver"
  subnet1 = "${module.vpc.subnet1}"
  subnet2 = "${module.vpc.subnet2}"
}
