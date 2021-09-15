# variable "upload_bucket" {
#   description = "S3 data ingestion bucket"
#   type        = string
# }

# variable "analyzed_bucket" {
#   description = "S3 analyzed data bucket"
#   type        = string
# }

# variable "image_name" {
#   type        = string
#   description = "docker image name"
# }

# variable "image_src" {
#   type        = string
#   description = "docker image src dir"
# }

# variable "role_arn" {
#   type        = string
#   description = "role arn w/permission to assume role"
# }

variable "sdk_upload_function_name" {
  type        = string
  description = "sdk upload lambda name"
}


variable "sdk_upload_invoke_arn" {
  type        = string
  description = "sdk upload lambda function invoke arn"
}

variable "get_sdk_status_function_name" {
  type        = string
  description = "get SDK status lambda name"
}

variable "get_sdk_status_invoke_arn" {
  type        = string
  description = "get SDK status function invoke arn"
}


# variable "function_description" {
#   type        = string
#   description = "lambda description"
# }
