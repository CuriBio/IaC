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

variable "function_name" {
  type        = string
  description = "lambda name"
}

variable "function_description" {
  type        = string
  description = "lambda description"
}

variable "lambda_env" {
  type = map
  description = "lambda env"
}

variable "allowed_triggers" {
  type = map
  description = "triggers"
  default = {}
}

variable "lambda_role" {
  type = string
  description = "lambda role"
  default = null
}

variable "attach_policies" {
  type = map
  description = "lambda policies"
  default = {}
}
