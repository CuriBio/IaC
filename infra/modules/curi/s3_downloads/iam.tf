resource "aws_iam_role" "downloads_role" {
  name = "s3_downloads_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = var.principals
        }
        Condition = {}
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_downloads" {
  name = "s3_downloads_policy"
  role = aws_iam_role.downloads_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = aws_s3_bucket.downloads.arn
      },
      {
        Action = [
          "s3:GetObjectAcl",
          "s3:GetBucketObjectLockConfiguration",
          "s3:GetObjectVersionTagging",
          "s3:GetBucketVersioning",
          "s3:GetBucketAcl",
          "s3:GetObjectTorrent",
          "s3:GetBucketCORS",
          "s3:GetBucketLocation",
          "s3:GetObjectVersion",
          "s3:GetBucketRequestPayment",
          "s3:GetObjectTagging",
          "s3:GetMetricsConfiguration",
          "s3:GetBucketPublicAccessBlock",
          "s3:GetEncryptionConfiguration",
          "s3:DeleteObjectVersion",
          "s3:GetBucketLogging",
          "s3:ListBucketVersions",
          "s3:GetAnalyticsConfiguration",
          "s3:GetObjectVersionForReplication",
          "s3:GetLifecycleConfiguration",
          "s3:ListBucketByTags",
          "s3:GetInventoryConfiguration",
          "s3:GetBucketTagging",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:GetObjectVersionTagging",
          "s3:GetObjectAcl",
          "s3:GetBucketObjectLockConfiguration",
          "s3:GetObjectVersionAcl",
          "s3:PutObjectTagging",
          "s3:DeleteObject",
          "s3:DeleteObjectTagging",
          "s3:GetBucketPolicyStatus",
          "s3:GetObjectRetention",
          "s3:GetBucketWebsite",
          "s3:DeleteObjectVersionTagging",
          "s3:GetObjectLegalHold",
          "s3:GetBucketNotification",
          "s3:GetReplicationConfiguration"
        ]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.downloads.arn}/*"
      },
      {
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation",
          "cloudfront:ListInvalidations"
        ]
        Effect   = "Allow"
        Resource = aws_cloudfront_distribution.s3_distribution.arn
      },
    ]
  })
}
