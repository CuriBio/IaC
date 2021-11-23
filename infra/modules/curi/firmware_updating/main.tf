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

# module "lambda" {
#   source = "../lambda"

#   #assume role for docker push
#   role_arn = var.role_arn

#   # docker image
#   image_name = var.image_name
#   image_src  = "../../src/lambdas/get_latest_firmware"

#   # lambda
#   function_name        = var.function_name
#   function_description = "Get upload/analysis status of files"

#   source_arn         = var.api_gateway_source_arn
#   lambda_api_gw_id   = var.lambda_api_gw_id
#   integration_method = "GET"
#   route_key          = "GET /firmware_latest"
#   authorizer_id      = var.authorizer_id
#   authorization_type = var.authorization_type
# }

# module "lambda" {
#   source = "../lambda"

#   #assume role for docker push
#   role_arn = var.role_arn

#   # docker image
#   image_name = var.image_name
#   image_src  = "../../src/lambdas/get_firmware_download"

#   # lambda
#   function_name        = var.function_name
#   function_description = "Get upload/analysis status of files"

#   source_arn         = var.api_gateway_source_arn
#   lambda_api_gw_id   = var.lambda_api_gw_id
#   integration_method = "GET"
#   route_key          = "GET /firmware_download"
#   authorizer_id      = var.authorizer_id
#   authorization_type = var.authorization_type
# }
