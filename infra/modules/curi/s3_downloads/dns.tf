# if creating for first time and domain was registered in route53
# this zone needs to be imported into terraform state otherwise this
# will create a second zone with the same domain b/c route53
# automatically creates a hosted zone for any domain you register
#
# from your workspace run `terraform import -var-file=./<workspace>/terraform.tfvars aws_route53_zone.main <HOSTED ZONE ID>`
resource "aws_route53_zone" "main" {
  name = var.hosted_zone
}


resource "aws_acm_certificate" "cert" {
  domain_name       = "*.${var.hosted_zone}"
  validation_method = "DNS"

  tags = {
    Environment = terraform.workspace
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cname_ssl_verification : record.fqdn]
}


resource "aws_route53_record" "cname" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "${var.subdomain}.${var.hosted_zone}"
  type    = "CNAME"
  ttl     = 86400
  records = [aws_cloudfront_distribution.s3_distribution.domain_name]
}


resource "aws_route53_record" "cname_ssl_verification" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}


resource "aws_route53_record" "a_record" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.hosted_zone
  type    = "A"
  ttl     = 3600

  # For Square space
  records = [
    "216.239.32.21",
    "216.239.34.21",
    "216.239.36.21",
    "216.239.38.21"
  ]
}


resource "aws_route53_record" "mx_record" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.hosted_zone
  type    = "MX"
  ttl     = "300"

  records = [
    "1 ASPMX.L.GOOGLE.COM.",
    "5 ALT1.ASPMX.L.GOOGLE.COM.",
    "5 ALT2.ASPMX.L.GOOGLE.COM.",
    "10 ALT3.ASPMX.L.GOOGLE.COM.",
    "10 ALT4.ASPMX.L.GOOGLE.COM."
  ]
}


resource "aws_route53_record" "google_site_verification" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.hosted_zone
  type    = "TXT"
  ttl     = 300

  records = [
    "google-site-verification=6G3CjRrIZseGdKwXTXBshjzVVPtGtfN0R57aTtioRC4"
  ]
}

resource "aws_route53_record" "github_verification" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "_github-challenge-curibio.www.curibio.com"
  type    = "TXT"
  ttl     = 60

  records = [
    "0bf388b617"
  ]
}
