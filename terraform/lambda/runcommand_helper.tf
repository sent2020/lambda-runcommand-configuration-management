# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

# Add Lambda basic policy for logging
resource "aws_iam_role_policy" "logging_policy" {
    name = "logging_policy"
    role = "${aws_iam_role.lambda_role.id}"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Add CodePipeline custom action policy
# CodePipeline currently requires codepipeline:* to get and put properly :(
resource "aws_iam_role_policy" "codepipeline_policy" {
    name = "codepipeline_policy"
    role = "${aws_iam_role.lambda_role.id}"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "codepipeline:*",
      "Resource": "*"
    }
  ]
}
EOF
}

# Add an SSM Policy
resource "aws_iam_role_policy" "ssm_policy" {
    name = "ssm_policy"
    role = "${aws_iam_role.lambda_role.id}"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:*",
        "ec2:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role" "lambda_role" {
    name = "garlc_runcommand_helper_lambda_role"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
output "lambda_role_arn" {
  value = "${aws_iam_role.lambda_role.name}"
}

# Lambda Function
resource "aws_lambda_function" "lambda_function" {
    filename = "lambda_runcommand_helper_payload.zip"
    function_name = "garlc_runcommand_helper"
    role = "${aws_iam_role.lambda_role.arn}"
    handler = "runcommand_helper.handle"
    description = "Invoked by GARLC to execute RunCommand for batches of Instances"
    memory_size = 128
    runtime = "python2.7"
    timeout = 300
    source_code_hash = "${base64sha256(file("lambda_runcommand_helper_payload.zip"))}"
}
