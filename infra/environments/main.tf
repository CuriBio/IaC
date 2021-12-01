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
variable "instance_class" {}
variable "db_creds_arn" {}

#jump host
variable "jump_host" {}
variable "jump_ec2_arn" {}

# upload/analysis status
variable "get_sdk_status_image_name" {}
variable "get_sdk_status_function_name" {}

# auth
variable "get_auth_image_name" {}
variable "get_auth_function_name" {}

# firmware updating
variable "main_firmware_bucket" {}
variable "channel_firmware_bucket" {}
variable "get_latest_firmware_image_name" {}
variable "get_latest_firmware_function_name" {}
variable "firmware_download_image_name" {}
variable "firmware_download_function_name" {}


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
  version_tag    = "v0.16.2"
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
  lambda_api_gw_id       = module.api.api_id
  authorizer_id          = module.api.authorizer_id
  authorization_type     = "JWT"

  db_creds_arn        = var.db_creds_arn
  db_cluster_endpoint = module.aurora_database.cluster_endpoint
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
  lambda_api_gw_id       = module.api.api_id
  authorizer_id          = module.api.authorizer_id
  authorization_type     = "JWT"
}

module "aurora_database" {
  source = "../modules/curi/aurora_rds"

  instance_class = var.instance_class
  db_creds_arn   = var.db_creds_arn
}

module "get_auth" {
  source = "../modules/curi/get_auth"

  # assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = "${terraform.workspace}-${var.get_auth_image_name}"

  # lambda
  function_name        = "${terraform.workspace}-${var.get_auth_function_name}"
  function_description = "Get auth tokens lambda"

  client_id              = module.api.cognito_pool_client_id
  api_gateway_source_arn = module.api.source_arn
  lambda_api_gw_id       = module.api.api_id
}


module "sdk_status_db" {
  source = "../modules/curi/sdk_status_db"
}


module "api" {
  source = "../modules/curi/api_gateway"
}


module "api_dns" {
  source = "../modules/curi/api_gateway_dns"
  count  = contains(["prod", "modl", "test"], terraform.workspace) ? 1 : 0

  lambda_api_gw_id    = module.api.api_id
  lambda_api_stage_id = module.api.api_stage_id

  hosted_zone  = var.hosted_zone
  subdomain    = "api"
  ssl_cert_arn = module.downloads[0].ssl_cert_arn
}


module "firmware_updating" {
  source = "../modules/curi/firmware_updating"

  # assume role for docker push
  role_arn = var.role_arn

  # s3 buckets
  main_firmware_bucket    = "${terraform.workspace}-${var.main_firmware_bucket}"
  channel_firmware_bucket = "${terraform.workspace}-${var.channel_firmware_bucket}"

  # docker images
  image_name_glf = "${terraform.workspace}-${var.get_latest_firmware_image_name}"
  image_name_fd  = "${terraform.workspace}-${var.firmware_download_image_name}"

  # lambdas
  function_name_glf        = "${terraform.workspace}-${var.get_latest_firmware_function_name}"
  function_description_glf = "Get latest firmware lambda"

  function_name_fd        = "${terraform.workspace}-${var.firmware_download_function_name}"
  function_description_fd = "Firmware download lambda"

  api_gateway_source_arn = module.api.source_arn
  lambda_api_gw_id       = module.api.api_id
  authorizer_id          = module.api.authorizer_id
  authorization_type     = "JWT"
}
