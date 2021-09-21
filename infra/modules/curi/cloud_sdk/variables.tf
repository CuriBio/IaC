variable "upload_bucket" {
  description = "S3 data ingestion bucket"
  type        = string
}

variable "analyzed_bucket" {
  description = "S3 analyzed data bucket"
  type        = string
}

variable "image_name" {
  type        = string
  description = "docker image name"
}

# variable "image_src" {
#   type        = string
#   description = "docker image src dir"
# }

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
