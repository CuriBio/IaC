variable "instance_type" {
  description = "RDS instance type and size"
  type        = string
}

variable "master_username" {
  description = "RDS username"
  type        = string
  sensitive   = true
}

variable "master_password" {
  description = "RDS password"
  type        = string
  value       = "testDBsetup1234"
  sensitive   = true
}
