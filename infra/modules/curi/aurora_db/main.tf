locals {
  name = "${terraform.workspace}-mantarray_db"
  region = "us_east_1"
  tags = {
    Application = "mantarray_db"
    Environment = "${terraform.workspace}"
  }
}
resource "aws_db_parameter_group" "parameter_group" {
  name = "${local.name}-parameter-group"
  family = "aurora-mysql5.7"
  description = "${local.name}-parameter-group"
  tags = local.tags
}
resource "aws_rds_cluster_parameter_group" "cluster_parameter_group" {
  name = "${local.name}-cluster-parameter-group"
  family = "aurora-mysql5.7"
  description = "${local.name}-cluster-parameter-group"
  tags = local.tags
}
# Providing a reference to our default VPC
resource "aws_default_vpc" "default_vpc" {
}
# Providing a reference to our default subnets
resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "${local.region}a"
}
resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "${local.region}b"
}
resource "aws_default_subnet" "default_subnet_c" {
  availability_zone = "${local.region}c"
}
module "aurora_db" {
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 3.0"

  name = "${local.name}"
  engine = "aurora-mysql"
  engine_version = "5.7.12"
  instance_type = "db.t3.small"
  instance_type_replica = "db.t3.small"

  vpc_id = aws_default_vpc.default_vpc.id
  subnets = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id, aws_default_subnet.default_subnet_c.id]
  allowed_cidr_blocks = aws_default_vpc.default_vpc.cidr_block

  apply_immediately = true
  skip_final_snapshot = true

  db_parameter_group_name = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]
  
  tags = local.tags
}
