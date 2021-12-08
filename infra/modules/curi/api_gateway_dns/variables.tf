variable "ssl_cert_arn" {
  description = "SSL cert arn for hosted zone"
  type        = string
}

variable "hosted_zone" {
  description = "AWS hosted zone name"
  type        = string
}

variable "subdomain" {
  description = "Subdomain"
  type        = string
}

variable "lambda_api_gw_id" {
  description = "Lambda API Gateway ID"
  type        = string
}

variable "lambda_api_stage_id" {
  description = "Lambda API Gateway Stage ID"
  type        = string
}
