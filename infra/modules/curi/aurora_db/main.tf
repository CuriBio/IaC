locals {
  name   = "${terraform.workspace}-mantarray_db"
  region = "us_east_1"
  tags = {
    Application = "mantarray_db"
    Environment = terraform.workspace
  }
}
provider "aws" {
  region = local.region
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
  availability_zone = "${local.region}a"
}
resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "${local.region}b"
}
module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name                  = local.name
  engine                = "aurora-mysql"
  engine_version        = "5.7.mysql_aurora.2.09.2"
  instance_type_replica = var.instance_type

  vpc_id              = aws_default_vpc.default_vpc.id
  subnets             = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id]
  allowed_cidr_blocks = [aws_default_vpc.default_vpc.cidr_block]

  replica_count = 1

  username = var.master_username

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}
