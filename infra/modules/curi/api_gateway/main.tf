resource "aws_apigatewayv2_api" "lambda_gw" {
  name          = "${terraform.workspace}-lambda-gw"
  protocol_type = "HTTP"
}

resource "aws_cognito_user_pool" "lambda_gw_pool" {
  name = "${terraform.workspace}-lambda-gw-pool"
}

resource "aws_cognito_user_pool_client" "lambda_gw_pool_client" {
  name         = "${terraform.workspace}-lambda-gw-pool-client"
  user_pool_id = aws_cognito_user_pool.lambda_gw_pool.id

  explicit_auth_flows = ["USER_PASSWORD_AUTH"]
}

resource "aws_apigatewayv2_authorizer" "lambda_gw_auth" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${terraform.workspace}-lambda-gw-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.lambda_gw_pool_client.id]
    issuer   = "https://${aws_cognito_user_pool.lambda_gw_pool.endpoint}"
  }
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/vendedlogs/${aws_apigatewayv2_api.lambda_gw.name}"
  tags = {
    Environment = terraform.workspace
    Application = "api-gw"
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "${terraform.workspace}-iam-for-lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_apigatewayv2_stage" "lambda_gw_stage" {
  api_id      = aws_apigatewayv2_api.lambda_gw.id
  name        = "${terraform.workspace}-lambda-gw-stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}
