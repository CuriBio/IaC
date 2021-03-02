provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = var.role_arn
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

resource "aws_ecr_repository" "ecr" {
  name                 = terraform.workspace
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
