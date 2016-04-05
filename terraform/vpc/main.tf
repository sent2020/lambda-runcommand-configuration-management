resource "aws_vpc" "garlc_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = "True"
  tags {
    Name = "garlc_vpc"
  }
}
output "vpc_id" {
  value = "${aws_vpc.garlc_vpc.id}"
}

resource "aws_subnet" "garlc_subnet1" {
    vpc_id = "${aws_vpc.garlc_vpc.id}"
    cidr_block = "10.0.0.0/17"
    map_public_ip_on_launch = "True"
    tags {
        Name = "garlc_pub_subnet1"
    }
}
resource "aws_route_table_association" "garlc_subnet1_route" {
    subnet_id = "${aws_subnet.garlc_subnet1.id}"
    route_table_id = "${aws_route_table.garlc_route.id}"
}
output "subnet1" {
  value = "${aws_subnet.garlc_subnet1.id}"
}

resource "aws_subnet" "garlc_subnet2" {
    vpc_id = "${aws_vpc.garlc_vpc.id}"
    cidr_block = "10.0.128.0/17"
    map_public_ip_on_launch = "True"
    tags {
        Name = "garlc_pub_subnet2"
    }
}
resource "aws_route_table_association" "garlc_subnet2_route" {
    subnet_id = "${aws_subnet.garlc_subnet2.id}"
    route_table_id = "${aws_route_table.garlc_route.id}"
}
output "subnet2" {
  value = "${aws_subnet.garlc_subnet2.id}"
}

resource "aws_internet_gateway" "garlc_gateway" {
    vpc_id = "${aws_vpc.garlc_vpc.id}"
    tags {
        Name = "garlc_igw"
    }
}

resource "aws_route_table" "garlc_route" {
    vpc_id = "${aws_vpc.garlc_vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.garlc_gateway.id}"
    }
    tags {
        Name = "garlc_route_table"
    }
}
