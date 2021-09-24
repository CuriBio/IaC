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

variable "get_auth_function_name" {
  type        = string
  description = "get auth lambda name"
}

variable "get_auth_invoke_arn" {
  type        = string
  description = "get auth function invoke arn"
}
