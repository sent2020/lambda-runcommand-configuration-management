resource "aws_iam_instance_profile" "profile" {
  name = "subiaco_instance_profile"
  roles = ["${aws_iam_role.role.name}"]
}

# Use the builtin AmazonEC2RoleforSSM
resource "aws_iam_policy_attachment" "policy" {
    name = "attach_ssm_policy"
    roles = ["${aws_iam_role.role.name}"]
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role" "role" {
  name = "subiaco_instance_role"
  path = "/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
output "profile_name" {
  value = "${aws_iam_instance_profile.profile.name}"
}
