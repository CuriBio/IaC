provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = "arn:aws:iam::245339368379:role/terraform_deploy_role"
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

module "data_ingest" {
  source                = "../../modules/curi/data_processor"
  data_processor_bucket = "curi-prod-data-test-bucket"
}
