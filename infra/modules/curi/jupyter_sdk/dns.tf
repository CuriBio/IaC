resource "aws_route53_record" "jupyter_cname" {
  allow_overwrite = true
  zone_id         = var.hosted_zone_id
  name            = "jupyter-sdk.${var.hosted_zone}"
  type            = "CNAME"
  ttl             = 3600
  records         = [aws_cloudfront_distribution.jupyter_sdk_distribution.domain_name]
}
