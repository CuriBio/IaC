variable "role_arn" {}
variable "image_name" {}
variable "data_bucket" {}
variable "function_name" {}


provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = var.role_arn
    session_name = "terraform"
  }
}


terraform {
  required_version = ">= 0.14.7"
  backend "s3" {
    bucket         = "curi-infrastructure-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}


module "lambda" {
  source = "../modules/curi/lambda"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.image_name}"
  image_src  = "../../src/lambdas/hello_world"

  # s3 bucket
  data_bucket = "${terraform.workspace}-${var.data_bucket}"

  #lambda
  function_name        = "${terraform.workspace}-${var.function_name}"
  function_description = "Hello world lambda"
}
