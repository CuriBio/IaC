resource "aws_s3_bucket" "log_bucket" {
  bucket = "curibio-${terraform.workspace}-server-access-logs"
}

resource "aws_s3_bucket_acl" "log_bucket" {
  bucket = aws_s3_bucket.log_bucket.id
  acl    = "log-delivery-write"
}


resource "aws_s3_bucket" "downloads" {
  bucket = "${var.subdomain}.${var.hosted_zone}"
}

resource "aws_s3_bucket_versioning" "downloads" {
  bucket = aws_s3_bucket.downloads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_logging" "downloads" {
  bucket = aws_s3_bucket.downloads.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "${var.subdomain}.${var.hosted_zone}_logs"
}

resource "aws_s3_bucket_website_configuration" "downloads" {
  bucket = aws_s3_bucket.downloads.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_acl" "downloads" {
  bucket = aws_s3_bucket.downloads.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "downloads_policy" {
  bucket = aws_s3_bucket.downloads.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "s3_downloads_policy"
    Statement = [
      {
        Sid       = "PublicReadGetObject",
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.downloads.arn}/*"
      },
    ]
  })
}
