variable "instance_type" {
  description = "RDS instance type and size"
  type        = string
}

variable "db_creds_arn" {
  description = "ARN value for db_creds secret"
  type        = string
}
variable "db_key_arn" {
  description = "Custom key attached to db to access endpoints in action"
  type        = string
}
