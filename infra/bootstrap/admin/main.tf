provider "aws" {
  region  = "us-east-1"
  profile = "curi_admin"
}

terraform {
  required_version = "0.14.7"
  backend "s3" {}
}
