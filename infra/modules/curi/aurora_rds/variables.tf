variable "instance_type" {
  description = "RDS instance type and size"
  type        = string
}

variable "db_username" {
  description = "RDS username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "RDS password"
  type        = string
  sensitive   = true
}

variable "key_pair_name" {
  description = "RDS password"
  default     = "db_key_pair"
  sensitive   = true
}
