generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
provider "aws" {
  region  = "us-east-1"
  assume_role {
    role_arn     = ""
    session_name = "terraform"
  }
}
EOF
}


generate "terraform" {
  path = "terraform.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}
EOF
}


remote_state {
  backend = "s3"
  config = {
    bucket = "curi-terraform-state"

    key            = "modl/${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}
