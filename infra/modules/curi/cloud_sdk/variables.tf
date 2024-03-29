variable "upload_bucket" {
  description = "S3 data ingestion bucket"
  type        = string
}

variable "analyzed_bucket" {
  description = "S3 analyzed data bucket"
  type        = string
}
variable "logs_bucket" {
  description = "S3 mantarray logs bucket"
  type        = string
}

variable "image_name" {
  type        = string
  description = "docker image name"
}

variable "lambda_api_gw_id" {
  type        = string
  description = "lambda api gateway id"
}

variable "api_gateway_source_arn" {
  type        = string
  description = "api gateway source arn"
}

variable "authorizer_id" {
  type        = string
  description = "authorizer id"
  default     = ""
}

variable "authorization_type" {
  type        = string
  description = "authorization type"
  default     = "NONE"
}

variable "role_arn" {
  type        = string
  description = "role arn w/permission to assume role"
}

variable "function_name" {
  type        = string
  description = "lambda name"
}

variable "function_description" {
  type        = string
  description = "lambda description"
}

variable "sdk_status_table_name" {
  type        = string
  description = "name of the SDK status table"
}

variable "sdk_status_table_arn" {
  type        = string
  description = "arn of the SDK status table"
}

variable "db_creds_arn" {
  description = "ARN value for db_creds secret"
  type        = string
}

variable "db_cluster_endpoint" {
  description = "database endpoint"
  type        = string
}
