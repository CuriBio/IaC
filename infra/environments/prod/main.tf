locals {
  role_arns = {
    "modl"  = "arn:aws:iam::725604423866:role/terraform_deploy_role"
    "prod"  = "arn:aws:iam::245339368379:role/terraform_deploy_role"
  }

  env      = terraform.workspace
  role_arn = local.role_arns[local.env]
}

provider "aws" {
  region = "us-east-1"

  assume_role {
    role_arn     = local.role_arn
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

module "data_ingest" {
  source                = "../../modules/curi/data_processor"
  data_processor_bucket = "curi-${local.env}-data-test-bucket"
}
