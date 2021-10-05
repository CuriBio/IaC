variable "image_name" {
  type        = string
  description = "docker image name"
}

variable "image_src" {
  type        = string
  description = "docker image src dir"
}

variable "role_arn" {
  type        = string
  description = "role arn w/permission to assume role"
}

variable "source_arn" {
  type = string
  description = "api gateway source arn"
}

variable "lambda_api_gw_id" {
  type = string
  description = "lambda api gateway id"
}

variable "integration_method" {
  type = string
  description = "lambda api integration method"
}

variable "authorizer_id" {
  type = string
  description = "authorizer id"
  default = ""
}

variable "authorization_type" {
  type = string
  description = "authorization type"
  default = ""
}

variable "route_key" {
  type = string
  description = "api route key"
}

variable "function_name" {
  type        = string
  description = "lambda name"
}

variable "function_description" {
  type        = string
  description = "lambda description"
}

variable "lambda_env" {
  type        = map(any)
  description = "lambda env"
}

variable "allowed_triggers" {
  type        = map(any)
  description = "triggers"
  default     = {}
}

variable "lambda_role" {
  type        = string
  description = "lambda role"
  default     = null
}

variable "attach_policies" {
  type        = map(any)
  description = "lambda policies"
  default     = {}
}
