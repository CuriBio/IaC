locals {
  name   = "${terraform.workspace}-mantarray-db"
  region = "us-east-1"
  tags = {
    Application = "mantarray-db"
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

module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = local.name
  engine         = "aurora-mysql"
  engine_version = "5.7.mysql_aurora.2.09.2"
  instance_type  = var.instance_type

  vpc_id = aws_default_vpc.default_vpc.id

  replica_count     = 1
  apply_immediately = true

  username = var.master_username

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}
