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

  lambda_env = {}

  # attach_policies = {}
}
