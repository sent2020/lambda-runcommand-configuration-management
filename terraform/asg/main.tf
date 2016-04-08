resource "aws_autoscaling_group" "asg" {
  lifecycle { create_before_destroy = true }
  name = "${var.asg_name}"
  launch_configuration = "${var.lcid}"
  max_size = "${var.max_size}"
  min_size = "${var.min_size}"
  desired_capacity = "${var.desired_capacity}"
  vpc_zone_identifier = ["${var.subnets}"]
  tag {
    key = "Ansible_Roles"
    value = "${var.ansible_roles}"
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
