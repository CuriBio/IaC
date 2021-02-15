provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "curi-dev-test"

  tags = {
    Name        = "curi-prod-test"
    Environment = "test"
  }
}

terraform {
  backend "s3" {
    bucket = "curi-tf-state"
    key    = "test/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "curi-terraform-locks"
    encrypt        = true
  }
}
