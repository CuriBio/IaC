variable "hosted_zone" {
  description = "Hosted zone"
  type        = string
}

variable "version_tag" {
  description = "Github tag"
  type        = string
}

variable "hosted_zone_id" {
  description = "Hosted zone id"
  type        = string
}

variable "ssl_cert_arn" {
  description = "SSL cert arn for hosted zone"
  type        = string
}
