variable "hosted_zone" {
  description = "AWS hosted zone name"
  type        = string
}

variable "subdomain" {
  description = "Subdomain"
  type        = string
}

variable "sqsp_verification" {
  description = "Squarespace verification"
  type        = string
}

variable "account_id" {
  description = "account_id of users to assume role"
  type        = string
}
