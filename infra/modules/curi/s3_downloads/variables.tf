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

variable "s3_download_users" {
  description = "s3 download bucket users"
  type        = list(any)
}
