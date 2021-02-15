provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "prod_bucket" {
  bucket = "curi-prod-test"

  tags = {
    Name        = "curi-prod-test"
    Environment = "prod"
  }
}

terraform {
  backend "s3" {
    bucket = "curi-tf-state"
    key = "prod/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "curi-terraform-locks"
    encrypt = true
  }
}

