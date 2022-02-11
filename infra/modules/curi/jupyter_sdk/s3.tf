resource "aws_cloudfront_distribution" "jupyter_sdk_distribution" {
  origin {
    domain_name = "jupyter-sdk.${var.hosted_zone}.s3-website-us-east-1.amazonaws.com"
    origin_id   = "website"

    custom_origin_config {
      origin_protocol_policy = "http-only"
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1.2", "TLSv1.1", "TLSv1"]
    }
  }


  enabled         = true
  is_ipv6_enabled = true
  comment         = "Managed by Terraform"

  aliases = ["jupyter-sdk.${var.hosted_zone}"]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "website"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 60
    max_ttl                = 86400
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = var.ssl_cert_arn
    ssl_support_method  = "sni-only"
  }
}

resource "aws_s3_bucket" "jupyter" {
  bucket = "jupyter-sdk.${var.hosted_zone}"
}

resource "aws_s3_bucket_website_configuration" "jupyter" {
  bucket = aws_s3_bucket.jupyter.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }

  routing_rule {
    redirect {
      http_redirect_code = "302"
      host_name          = "mybinder.org"
      replace_key_with   = "v2/gh/curibio/jupyter_sdk/${var.version_tag}?filepath=intro.ipynb"
    }
  }
}

resource "aws_s3_bucket_acl" "jupyter" {
  bucket = aws_s3_bucket.jupyter.id
  acl    = "public-read"
}
