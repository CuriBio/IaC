module "lambda" {
  source = "../lambda"

  #assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = var.image_name
  image_src  = "../../src/lambdas/sdk_upload"

  # lambda
  function_name        = var.function_name
  function_description = "Handle sdk data upload"

  # api gateway source arn
  source_arn         = var.api_gateway_source_arn
  lambda_api_gw_id   = var.lambda_api_gw_id
  integration_method = "POST"
  route_key          = "POST /sdk_upload"
  authorizer_id      = var.authorizer_id
  authorization_type = var.authorization_type

  # attach_policy = aws_iam_role.policy.arn
  # depends_on = [aws_iam_role_policy_attachment.lambda-attach]

  lambda_env = {
    SQS_NAME         = "${terraform.workspace}-sdk-upload-queue",
    S3_BUCKET        = var.upload_bucket,
    SDK_STATUS_TABLE = var.sdk_status_table_name,
    #REGION = var.aws_region
  }

  # allowed_triggers = {
  #   S3Upload = {
  #     service    = "s3"
  #     source_arn = aws_s3_bucket.upload_bucket.arn
  #   }
  # }
  attach_policies = {
    s3_put = {
      effect    = "Allow",
      actions   = ["s3:PutObject"],
      resources = ["${aws_s3_bucket.upload_bucket.arn}/*"]
    },
    dynamodb_put = {
      effect    = "Allow",
      actions   = ["dynamodb:PutItem"],
      resources = [var.sdk_status_table_arn]
    },
  }
}

module "ecs_task" {
  source   = "../ecs_task"
  role_arn = var.role_arn

  image_name = "sdk_analysis"
  image_src  = "../../src/lambdas/sdk_analysis"

  task_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
        ]
        Effect   = "Allow"
        Resource = aws_sqs_queue.sdk_upload_queue.arn
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.upload_bucket.arn,
          "${aws_s3_bucket.upload_bucket.arn}/*",
          aws_s3_bucket.analyzed_bucket.arn,
          "${aws_s3_bucket.analyzed_bucket.arn}/*",
        ]
      },
      {
        Action = [
          "dynamodb:UpdateItem",
        ]
        Effect   = "Allow"
        Resource = var.sdk_status_table_arn
      },
      {
        Action = [
          "secretsmanager:GetSecretValue",
        ]
        Effect   = "Allow"
        Resource = var.db_creds_arn
      },
      {
        Action = [
          "kms:*",
        ]
        Effect   = "Allow"
        Resource = [data.aws_kms_key.default_key_alias.arn, data.aws_kms_key.db_key_alias.arn]
      },
      {
        Action = [
          "rds:DescribeDBClusterEndpoints",
          "rds:DescribeDBInstances",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:rds:us-east-1:077346344852:*"
      },
    ]
  })

  task_env = [
    {
      "name" : "SQS_URL",
      "value" : aws_sqs_queue.sdk_upload_queue.url
    },
    {
      "name" : "S3_UPLOAD_BUCKET",
      "value" : aws_s3_bucket.analyzed_bucket.bucket
    },
    {
      "name" : "SDK_STATUS_TABLE",
      "value" : var.sdk_status_table_name,
    },
    {
      "name" : "DB_CLUSTER_ENDPOINT",
      "value" : var.db_cluster_endpoint
    }
  ]
}


# S3 upload bucket
resource "aws_s3_bucket" "upload_bucket" {
  bucket = var.upload_bucket
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket" "analyzed_bucket" {
  bucket = var.analyzed_bucket
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}


# SQS
resource "aws_sqs_queue" "sdk_queue_deadletter" {
  name = "${terraform.workspace}-sdk-queue-deadletter"
}

resource "aws_sqs_queue" "sdk_upload_queue" {
  name = "${terraform.workspace}-sdk-upload-queue"
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sdk_queue_deadletter.arn
    maxReceiveCount     = 4
  })

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:*:*:${terraform.workspace}-sdk-upload-queue",
      "Condition": {
        "ArnEquals": { "aws:SourceArn": "${aws_s3_bucket.upload_bucket.arn}" }
      }
    }
  ]
}
POLICY
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.upload_bucket.id

  queue {
    queue_arn = aws_sqs_queue.sdk_upload_queue.arn
    events    = ["s3:ObjectCreated:*"]
  }
}

data "aws_kms_key" "default_key_alias" {
  key_id = "alias/aws/rds"
}
data "aws_kms_key" "db_key_alias" {
  key_id = "alias/db-key"
}
