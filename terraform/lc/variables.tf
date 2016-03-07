variable "instance_type" {
  default = "t2.nano"
}
variable "amis" {
  default = {
    us-east-1 = "ami-60b6c60a"
  }
}
variable "iam_instance_profile" {}
variable "key_name" {}
variable "region" {}
