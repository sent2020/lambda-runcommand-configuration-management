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
resource "aws_iam_role_policy" "bootstrap_logging_policy" {
  name = "logging_policy"
  role = "${aws_iam_role.bootstrap_lambda_role.id}"
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

# Add S3 Get/List policy
resource "aws_iam_role_policy" "bootstrap_s3_policy" {
  name = "s3_policy"
  role = "${aws_iam_role.bootstrap_lambda_role.id}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
      "s3:ListAllMyBuckets",
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:GetObject"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Add CodePipeline custom action policy
# CodePipeline currently requires codepipeline:* to get and put properly :(
resource "aws_iam_role_policy" "bootstrap_codepipeline_policy" {
  name = "codepipeline_policy"
  role = "${aws_iam_role.bootstrap_lambda_role.id}"
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
resource "aws_iam_role_policy" "bootstrap_ssm_policy" {
  name = "ssm_policy"
  role = "${aws_iam_role.bootstrap_lambda_role.id}"
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

resource "aws_iam_role" "bootstrap_lambda_role" {
  name = "garlc_bootstrap_lambda_role"
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
output "bootstrap_lambda_role_arn" {
  value = "${aws_iam_role.bootstrap_lambda_role.name}"
}

# Lambda Function
resource "aws_lambda_function" "bootstrap_lambda_function" {
  filename = "lambda_bootstrap_payload.zip"
  function_name = "garlc_bootstrap"
  role = "${aws_iam_role.bootstrap_lambda_role.arn}"
  handler = "lambda_bootstrap.handle"
  description = "Bootstraps new instances with GARLC"
  memory_size = 128
  runtime = "python2.7"
  timeout = 300
  source_code_hash = "${base64sha256(file("lambda_bootstrap_payload.zip"))}"
}

output "bootstrap_lambda_name" {
  value = "{$aws_lambda_function.bootstrap_lambda_function.function_name}"
}

# CloudWatch Event Rule and Event Target
resource "aws_cloudwatch_event_rule" "instance_running" {
  depends_on = ["aws_iam_role.bootstrap_lambda_role"] # we need the Lambda arn to exist
  name = "garlc_bootstrap"
  description = "Trigger garlc_bootstrap function when a new instance enters the running state"
  event_pattern = <<PATTERN
  {
    "source": [ "aws.ec2" ],
    "detail-type": [ "EC2 Instance State-change Notification" ],
    "detail": {
      "state": [ "running" ]
    }
  }
PATTERN
}

resource "aws_lambda_permission" "allow_cloudwatch" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.bootstrap_lambda_function.arn}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.instance_running.arn}"
}

resource "aws_cloudwatch_event_target" "bootstrap_lambda" {
  depends_on = ["aws_iam_role.bootstrap_lambda_role"] # we need the Lambda arn to exist
  rule = "${aws_cloudwatch_event_rule.instance_running.name}"
  target_id = "garlc_bootstrap"
  arn = "${aws_lambda_function.bootstrap_lambda_function.arn}"
}
