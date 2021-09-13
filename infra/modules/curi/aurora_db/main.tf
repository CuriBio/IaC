locals {
  name = "${terraform.workspace}-mantarray-db"
  tags = {
    Application = "mantarray-db"
    Environment = terraform.workspace
  }
}
resource "random_password" "db_password" {
  length  = 10
  special = false
}
resource "aws_db_parameter_group" "parameter_group" {
  name        = "${local.name}-parameter-group"
  family      = "aurora-mysql5.7"
  description = "${local.name}-parameter-group"
  tags        = local.tags
}
resource "aws_rds_cluster_parameter_group" "cluster_parameter_group" {
  name        = "${local.name}-cluster-parameter-group"
  family      = "aurora-mysql5.7"
  description = "${local.name}-cluster-parameter-group"
  tags        = local.tags
}

# Providing a reference to our default VPC
resource "aws_default_vpc" "default_vpc" {}

# Providing a reference to our default subnets
resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "us-east-1a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "us-east-1b"
}

resource "aws_default_subnet" "default_subnet_c" {
  availability_zone = "us-east-1c"
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

resource "aws_security_group_rule" "egress" {
  description       = "Allow all egress traffic"
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.rds.id
}

module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = local.name
  engine         = "aurora-mysql"
  engine_version = "5.7.mysql_aurora.2.09.2"
  instance_type  = var.instance_type

  subnets                = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id]
  vpc_id                 = aws_default_vpc.default_vpc.id
  vpc_security_group_ids = [aws_default_vpc.default_vpc.default_security_group_id]

  replica_count       = 2
  apply_immediately   = true
  skip_final_snapshot = true

  username               = var.db_username
  password               = var.db_password
  create_random_password = false

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}
