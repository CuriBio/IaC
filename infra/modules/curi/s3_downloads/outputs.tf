output "hosted_zone_id" {
  value = aws_route53_zone.main.zone_id
}

output "ssl_cert_arn" {
  value = aws_acm_certificate.cert.arn
}
