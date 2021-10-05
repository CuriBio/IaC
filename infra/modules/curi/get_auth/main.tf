module "lambda" {
  source = "../lambda"

  #assume role for docker push
  role_arn = var.role_arn

  # docker image
  image_name = var.image_name
  image_src  = "../../src/lambdas/get_auth"

  # lambda
  function_name        = var.function_name
  function_description = "Get auth tokens"

  source_arn = var.api_gateway_source_arn
  lambda_api_gw_id = var.lambda_api_gw_id
  integration_method = "POST"
  route_key = "POST /get_auth"
  authorizer_id = var.authorizer_id
  authorization_type = var.authorization_type

  lambda_env = {
    COGNITO_USER_POOL_CLIENT_ID = var.client_id
  }

  # attach_policies = {}
}
