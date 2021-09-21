variable "image_name" {
  type        = string
  description = "docker image name"
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
