provider "aws" {
  region  = "us-east-1"
  profile = "curi_modl"
}

terraform {
  required_version = "0.14.7"
  backend "s3" {}
}

module "iam_roles" {
  source     = "../modules/aws/iam_role_policy"
  account_id = var.account_id
}
