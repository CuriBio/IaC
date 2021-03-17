resource "aws_s3_bucket" "log_bucket" {
  bucket = "curibio-${terraform.workspace}-server-access-logs"
  acl    = "log-delivery-write"
}

resource "aws_s3_bucket" "downloads" {
  bucket = "${var.subdomain}.${var.hosted_zone}"
  acl    = "public-read"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "PublicReadGetObject",
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "s3:GetObject"
        Resource = "arn:aws:s3:::${var.subdomain}.${var.hosted_zone}/*"
      }
    ]
  })

  versioning {
    enabled = true
  }

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  logging {
    target_bucket = aws_s3_bucket.log_bucket.id
    target_prefix = "${var.subdomain}.${var.hosted_zone}_logs"
  }
}
