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

#database
variable "instance_type" {}
variable "db_creds_arn" {}

# upload/analysis status
variable "get_sdk_status_image_name" {}
variable "get_sdk_status_function_name" {}

# auth
variable "get_auth_image_name" {}
variable "get_auth_function_name" {}


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
  version_tag    = "v0.17.1"
}


module "sdk_analysis" {
  source = "../modules/curi/cloud_sdk"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.sdk_upload_image_name}"

  # s3 buckets
  upload_bucket   = "${terraform.workspace}-${var.upload_bucket}"
  analyzed_bucket = "${terraform.workspace}-${var.analyzed_bucket}"

  # lambda
  function_name        = "${terraform.workspace}-${var.sdk_upload_function_name}"
  function_description = "SDK upload lambda"

  sdk_status_table_name = module.sdk_status_db.name
  sdk_status_table_arn  = module.sdk_status_db.arn

  api_gateway_source_arn = module.api.source_arn
  lambda_api_gw_id = module.api.api_id
  authorizer_id = module.api.authorizer_id
  authorization_type = "JWT"
}


module "get_sdk_status" {
  source = "../modules/curi/get_sdk_status"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.get_sdk_status_image_name}"

  # lambda
  function_name        = "${terraform.workspace}-${var.get_sdk_status_function_name}"
  function_description = "Upload/analysis status lambda"

  sdk_status_table_name = module.sdk_status_db.name
  sdk_status_table_arn  = module.sdk_status_db.arn

  api_gateway_source_arn = module.api.source_arn
  lambda_api_gw_id = module.api.api_id
  authorizer_id = module.api.authorizer_id
  authorization_type = "JWT"
}

module "aurora_database" {
  source = "../modules/curi/aurora_rds"

  instance_type = var.instance_type
  db_creds_arn = var.db_creds_arn
}

#module "lambda" {
#  source = "../modules/curi/lambda"

module "get_auth" {
  source = "../modules/curi/get_auth"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.get_auth_image_name}"

  # lambda
  function_name        = "${terraform.workspace}-${var.get_auth_function_name}"
  function_description = "Get auth tokens lambda"

  client_id = module.api.cognito_pool_client_id
  api_gateway_source_arn = module.api.source_arn
  lambda_api_gw_id = module.api.api_id
}


module "sdk_status_db" {
  source = "../modules/curi/sdk_status_db"
}


module "api" {
  source = "../modules/curi/api_gateway"

  #sdk_upload_function_name     = var.sdk_upload_function_name
  #sdk_upload_invoke_arn        = module.sdk_analysis.invoke_arn
  #get_sdk_status_function_name = var.get_sdk_status_function_name
  #get_sdk_status_invoke_arn    = module.get_sdk_status.invoke_arn
  #get_auth_function_name       = var.get_auth_function_name
  #get_auth_invoke_arn          = module.get_auth.invoke_arn
}
