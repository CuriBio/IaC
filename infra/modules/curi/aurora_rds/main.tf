locals {
  name = "${terraform.workspace}-mantarray-rds"
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.creds.secret_string
  )
  tags = {
    Application = "mantarray-rds"
    Environment = terraform.workspace
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

data "aws_secretsmanager_secret" "DBsecrets" {
  name = "db-creds"
}

data "aws_secretsmanager_secret_version" "creds" {
  secret_id = data.aws_secretsmanager_secret.DBsecrets.arn
}

module "rds" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = local.name
  engine         = "aurora-mysql"
  engine_version = "5.7.mysql_aurora.2.09.2"
  instance_type  = var.instance_type

  subnets                = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id]
  vpc_id                 = aws_default_vpc.default_vpc.id
  vpc_security_group_ids = [aws_default_vpc.default_vpc.default_security_group_id, aws_security_group.rds.id]
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
