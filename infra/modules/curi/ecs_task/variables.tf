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

variable "task_env" {
  type        = list(any)
  description = "task environment variables"
  default     = []
}

variable "task_policy" {
  type        = string
  description = "task role policy"
  default     = ""
}
