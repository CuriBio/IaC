
# Providing a reference to our default VPC
resource "aws_default_vpc" "default_vpc" {
  enable_dns_hostnames = true
  enable_dns_support   = true
}

# Providing a reference to our default subnets
resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "us-east-1a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "us-east-1b"
}

resource "aws_security_group" "rds" {
  description = "Allow inbound traffic from the security groups"
  vpc_id      = aws_default_vpc.default_vpc.id
}

resource "aws_security_group_rule" "ingress_cidr_blocks" {
  description       = "Allow all inbound traffic"
  type              = "ingress"
  from_port         = 3306
  to_port           = 3306
  protocol          = "tcp"
  cidr_blocks       = [aws_default_vpc.default_vpc.cidr_block]
  security_group_id = aws_security_group.rds.id
}

resource "aws_security_group" "ec2" {
  name   = "ec2_sg"
  vpc_id = aws_default_vpc.default_vpc.id

  # SSH access from the VPC
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}
