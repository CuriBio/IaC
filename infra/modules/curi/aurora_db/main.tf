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
resource "random_password" "master_password" {
  length = 10
}
# Data sources to get VPC and subnets
data "aws_vpc" "default" {
  default = true
}
data "aws_subnet_ids" "all" {
  vpc_id = data.aws_vpc.default.id
}
module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = local.name
  engine         = "aurora-mysql"
  engine_version = "5.7.mysql_aurora.2.09.2"
  instance_type  = var.instance_type

  subnets = data.aws_subnet_ids.all.ids
  vpc_id  = data.aws_vpc.default.id

  replica_count     = 1
  apply_immediately = true

  username               = var.master_username
  password               = random_password.master_password.result
  create_random_password = false

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}

resource "null_resource" "setup_db" {
  depends_on = [module.db] #wait for the db to be ready
  provisioner "local-exec" {
    command = "mysql -u ${module.db.username} -p ${random_password.master_password.result} -h ${aws_rds_cluster_instance.this.endpoint} < schema.sql"
  }
}
