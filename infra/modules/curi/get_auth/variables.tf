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

variable "client_id" {
  type        = string
  description = "cognito user pool client ID"
}