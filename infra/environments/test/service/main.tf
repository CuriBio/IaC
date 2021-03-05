locals {
  role_arn = "arn:aws:iam::077346344852:role/terraform_deploy_role"
  image_name = "${terraform.workspace}-hello_world"
  data_bucket = "${terraform.workspace}-test-data"
  function_name = "${terraform.workspace}-hello-lambda"
  function_description = "Hello world lambda"
}

provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = local.role_arn
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

module "lambda" {
  source = "../../../modules/curi/lambda"

  # assume role for docker push
  role_arn = local.role_arn

  # docker image
  image_name = local.image_name
  image_src  = "../../../../src/lambdas/hello_world"

  # s3 bucket
  data_bucket           = local.data_bucket

  #lambda
  function_name         = local.function_name
  function_description  = local.function_description
}
