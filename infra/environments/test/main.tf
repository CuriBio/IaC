provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = "arn:aws:iam::077346344852:role/terraform_deploy_role"
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

module "data_processor" {
  source                = "../../modules/curi/data_processor"
  data_processor_bucket = "curi-test-data-test-bucket3"
}
