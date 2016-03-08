variable "region" {
  default = "us-east-1"
}
variable "availability_zones" {
  # No spaces allowed between az names!
  default = "us-east-1a,us-east-1b,us-east-1d,us-east-1e"
}
variable "max_size" {
  default = "1"
}
variable "min_size" {
  default = "1"
}
variable "desired_capacity" {
  default = "1"
}
variable "lcid" {}
variable "asg_name" {}
variable "roles" {}
