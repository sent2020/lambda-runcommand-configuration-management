provider "aws" {
  region = "${var.region}"
}
resource "aws_vpc" "garlc-vpc" {
  cidr_block = "10.0.0.0/16"
  tags {
    Name = "garlc_vpc"
  }
}
resource "aws_subnet" "garlc-subnet" {
    vpc_id = "${aws_vpc.garlc-vpc.id}"
    cidr_block = "10.0.10.0/24"
    map_public_ip_on_launch = "True"
    enable_dns_hostnames = "True"
    tags {
        Name = "garlc_pub_subnet"
    }
}
resource "aws_internet_gateway" "garlc-gateway" {
    vpc_id = "${aws_vpc.garlc-vpc.id}"
    tags {
        Name = "garlc_igw"
    }
}
resource "aws_route_table" "garlc-route" {
    vpc_id = "${aws_vpc.garlc-vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.garlc-gateway.id}"
    }
    tags {
        Name = "garlc_route_table"
    }
}
output "vpcid" {
  value = "${aws_vpc.garlc-vpc.id}"
}
output "subnet" {
  value = "$aws_subnet.garlc-subnet.id"
}
