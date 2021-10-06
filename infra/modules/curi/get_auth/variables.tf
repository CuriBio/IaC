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

variable "client_id" {
  type        = string
  description = "cognito user pool client ID"
}
