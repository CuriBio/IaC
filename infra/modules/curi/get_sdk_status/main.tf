module "lambda" {
  source = "../lambda"

  #assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = var.image_name
  image_src  = "../../src/lambdas/get_sdk_status"

  # lambda
  function_name        = var.function_name
  function_description = "Get upload/analysis status of files"

  lambda_env = {
    SDK_STATUS_TABLE = var.sdk_status_table_name,
  }

  attach_policies = {
    dynamodb_get = {
      effect    = "Allow",
      actions   = ["dynamodb:GetItem"],
      resources = [var.sdk_status_table_arn]
    },
  }
}
