variable "instance_type" {
  default = "t2.nano"
}
variable "amis" {
  default = {
    us-west-2 = "ami-bf04f1df"
  }
}
variable "iam_instance_profile" {}
variable "key_name" {}
variable "region" {}
variable "vpc_id" {}
