variable "firmware_bucket" {
  description = "Firmware file bucket"
  type        = string
}

variable "image_name_glf" {
  type        = string
  description = "docker image name for get_latest_firmware"
}

variable "image_name_fd" {
  type        = string
  description = "docker image name for firmware_download"
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

variable "function_name_glf" {
  type        = string
  description = "get_latest_firmware lambda name"
}

variable "function_description_glf" {
  type        = string
  description = "get_latest_firmware lambda description"
}

variable "function_name_fd" {
  type        = string
  description = "firmware_download lambda name"
}

variable "function_description_fd" {
  type        = string
  description = "firmware_download lambda description"
}
