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
resource "aws_default_vpc" "default_vpc" {
}

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

module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = local.name
  engine         = "aurora-mysql"
  engine_version = "5.7.mysql_aurora.2.09.2"
  instance_type  = var.instance_type

  subnets = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id, aws_default_subnet.default_subnet_c.id]
  vpc_id  = aws_default_vpc.default_vpc.id

  replica_count     = 1
  apply_immediately = true

  username               = var.db_username
  password               = var.db_password
  create_random_password = false
  publicly_assessible    = true

  db_parameter_group_name         = aws_db_parameter_group.parameter_group.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.id

  tags = local.tags
}

resource "null_resource" "setup_db" {
  depends_on = [module.db]
  provisioner "local-exec" {
    command = "mysql -u $USERNAME -h $HOST -P $PORT -p$PASSWORD < ${path.module}/schema.sql;"
    environment = {
      USERNAME = format(var.db_username)
      HOST     = module.db.rds_cluster_instance_endpoints[0]
      PORT     = module.db.rds_cluster_port
      PASSWORD = format(var.db_password)
    }
  }
}
