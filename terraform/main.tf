provider "aws" {
  region = "${var.region}"
}

module "instance_profile" {
  source = "./iam"
}

module "lambda" {
  source = "./lambda"
}

module "launch_configuration" {
  source = "./lc"
  iam_instance_profile = "${module.instance_profile.profile_name}"
  region = "${var.region}"
  key_name = "joshcb"
}

module "webserver_asg" {
  source = "./asg"
  lcid = "${module.launch_configuration.lcid}"
  max_size = 50
  min_size = 2
  desired_capacity = 2
  asg_name = "garlc_webservers"
  roles = "webserver,appserver"
}

module "database_asg" {
  source = "./asg"
  lcid = "${module.launch_configuration.lcid}"
  max_size = 5
  min_size = 1
  desired_capacity = 1
  asg_name = "garlc_databases"
  roles = "dbserver"
}
