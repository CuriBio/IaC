# lambda variables
variable "role_arn" {}
variable "image_name" {}
variable "data_bucket" {}
variable "function_name" {}

# download/dns variables
variable "hosted_zone" {}

# squarespace
variable "sqsp_verification" {}

# cloud sdk
variable "upload_bucket" {}
variable "analyzed_bucket" {}
variable "sdk_upload_image_name" {}
variable "sdk_upload_function_name" {}


terraform {
  required_version = ">= 0.14.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.35.0"
    }
  }

  backend "s3" {
    bucket         = "curi-infrastructure-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}


provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = var.role_arn
    session_name = "terraform"
  }
}


module "downloads" {
  source = "../modules/curi/s3_downloads"
  count  = contains(["prod", "modl", "test"], terraform.workspace) ? 1 : 0

  # hosted zone
  hosted_zone = var.hosted_zone
  subdomain   = "downloads"

  # squarespace dns verification
  sqsp_verification = var.sqsp_verification

  # account principals for role policy of s3 downloads
  principals = [
    "arn:aws:iam::424924102580:root",
    "arn:aws:iam::750030001816:root"
  ]
}


module "jupyter_notebook" {
  source = "../modules/curi/jupyter_sdk"
  count  = contains(["prod", "modl", "test"], terraform.workspace) ? 1 : 0

  hosted_zone    = var.hosted_zone
  hosted_zone_id = module.downloads[0].hosted_zone_id
  ssl_cert_arn   = module.downloads[0].ssl_cert_arn
  version_tag    = "v0.16.1"
}


module "sdk_analysis" {
  source = "../modules/curi/cloud_sdk"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.sdk_upload_image_name}"

  # s3 buckets
  upload_bucket = "${terraform.workspace}-${var.upload_bucket}"
  analyzed_bucket = "${terraform.workspace}-${var.analyzed_bucket}"

  #lambda
  function_name        = "${terraform.workspace}-${var.sdk_upload_function_name}"
  function_description = "SDK upload lambda"
}

#module "lambda" {
#  source = "../modules/curi/lambda"

#  # assume role for docker push
#  role_arn = var.role_arn

#  # docker image
#  image_name = "${terraform.workspace}-${var.image_name}"
#  image_src  = "../../src/lambdas/hello_world"

#  # s3 bucket
#  data_bucket = "${terraform.workspace}-${var.data_bucket}"

#  #lambda
#  function_name        = "${terraform.workspace}-${var.function_name}"
#  function_description = "Hello world lambda"

#  lambda_env = {
#    WORKSPACE = terraform.workspace
#  }
#}
