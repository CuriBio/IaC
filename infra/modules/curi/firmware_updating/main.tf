resource "aws_s3_bucket" "firmware_bucket" {
  bucket = var.firmware_bucket
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

module "lambda_glf" {
  source = "../lambda"

  #assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = var.image_name_glf
  image_src  = "../../src/lambdas/get_latest_firmware"

  # lambda
  function_name        = var.function_name_glf
  function_description = "Get latest firmware version"

  source_arn         = var.api_gateway_source_arn
  lambda_api_gw_id   = var.lambda_api_gw_id
  integration_method = "POST"
  route_key          = "GET /firmware_latest"
  authorizer_id      = ""
  authorization_type = "NONE"

  lambda_env = {
    S3_BUCKET = var.firmware_bucket
  }

  attach_policies = {
    s3 = {
      effect = "Allow",
      actions = [
        "s3:ListBucket",
        "s3:GetObject",
      ],
      resources = [
        aws_s3_bucket.firmware_bucket.arn,
        "${aws_s3_bucket.firmware_bucket.arn}/*"
      ]
    },
  }
}


module "lambda_fd" {
  source = "../lambda"

  #assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = var.image_name_fd
  image_src  = "../../src/lambdas/firmware_download"

  # lambda
  function_name        = var.function_name_fd
  function_description = "Download given firmware version"

  source_arn         = var.api_gateway_source_arn
  lambda_api_gw_id   = var.lambda_api_gw_id
  integration_method = "POST"
  route_key          = "GET /firmware_download"
  authorizer_id      = var.authorizer_id
  authorization_type = var.authorization_type

  lambda_env = {
    S3_BUCKET = var.firmware_bucket
  }

  attach_policies = {
    s3 = {
      effect = "Allow",
      actions = [
        "s3:GetObject",
      ],
      resources = [
        aws_s3_bucket.firmware_bucket.arn,
        "${aws_s3_bucket.firmware_bucket.arn}/*"
      ]
    },
  }
}
