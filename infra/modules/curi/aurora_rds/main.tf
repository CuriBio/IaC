locals {
  name = "${terraform.workspace}-mantarray-db"
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.db_creds.secret_string
  )
  tags = {
    Application = "mantarray-db"
    Identifier = terraform.workspace
  }
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


data "aws_secretsmanager_secret" "db_secret" {
  name = "db-creds"
}

data "aws_secretsmanager_secret_version" "db_creds" {
  secret_id = data.aws_secretsmanager_secret.db_secret.arn
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
  create_security_group  = false

  replica_count       = 1
  apply_immediately   = true
  skip_final_snapshot = true

  username               = local.db_creds.username
  password               = local.db_creds.password
  create_random_password = false

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}
