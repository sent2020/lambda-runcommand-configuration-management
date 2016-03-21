resource "aws_launch_configuration" "garlc" {
  lifecycle { create_before_destroy = true }
  name_prefix = "garlc-"
  image_id = "${lookup(var.amis, var.region)}"
  enable_monitoring = true
  instance_type = "${var.instance_type}"
  security_groups = [
    "${aws_security_group.garlc_demo_sg.id}"
  ]
  user_data = "${file("${path.module}/userdata.sh")}"
  key_name = "${var.key_name}"
  iam_instance_profile = "${var.iam_instance_profile}"
}
output "lcid" {
  value = "${aws_launch_configuration.garlc.id}"
}

resource "aws_security_group" "garlc_demo_sg" {
  name = "garlc_demo_sg"
  description = "Demo SG this ol boy aint secure"
  vpc_id = "${var.vpc_id}"
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
      Name = "garlc_demo_sg"
  }
}
