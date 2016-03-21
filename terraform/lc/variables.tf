variable "instance_type" {
  default = "t2.nano"
}
variable "amis" {
  default = {
    us-east-1 = "ami-60b6c60a"
    us-west-2 = "ami-63b25203"
  }
}
variable "iam_instance_profile" {}
variable "key_name" {}
variable "region" {}
variable "vpc_id" {}
