provider "aws" {
  region = "${var.region}"
}

resource "aws_autoscaling_group" "asg" {
  lifecycle { create_before_destroy = true }
  name = "${var.asg_name}"
  availability_zones = ["${split(",", var.availability_zones)}"]
  launch_configuration = "${var.lcid}"
  max_size = "${var.max_size}"
  min_size = "${var.min_size}"
  desired_capacity = "${var.desired_capacity}"
  tag {
    key = "Roles"
    value = "${var.roles}"
    propagate_at_launch = true
  }
  tag {
    key = "has_ssm_agent"
    value = "true"
    propagate_at_launch = true
  }
}

output "asgid" {
  value = "${aws_autoscaling_group.asg.name}"
}
