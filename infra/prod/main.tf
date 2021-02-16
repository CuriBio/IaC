provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "prod_bucket" {
  bucket = "curi-prod-test"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Name        = "curi-prod-test"
    Environment = "prod"
  }
}

terraform {
  required_version = "0.14.6"

  backend "s3" {
    bucket = "curi-tf-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "curi-terraform-locks"
    encrypt        = true
  }
}

