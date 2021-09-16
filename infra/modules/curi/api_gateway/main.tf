resource "aws_apigatewayv2_api" "lambda_gw" {
  name          = "${terraform.workspace}-lambda-gw"
  protocol_type = "HTTP"
}

resource "aws_cognito_user_pool" "lambda_gw_pool" {
  name = "${terraform.workspace}-lambda-gw-pool"
}

resource "aws_cognito_user_pool_client" "lambda_gw_pool_client" {
  name = "${terraform.workspace}-lambda-gw-pool-client"

  user_pool_id = aws_cognito_user_pool.lambda_gw_pool.id

  # allowed_oauth_flows_user_pool_client = true
  # allowed_oauth_flows - (Optional) List of allowed OAuth flows (code, implicit, client_credentials).
  # allowed_oauth_scopes - (Optional) List of allowed OAuth scopes (phone, email, openid, profile, and aws.cognito.signin.user.admin).
  explicit_auth_flows = ["USER_PASSWORD_AUTH"]
}

resource "aws_apigatewayv2_authorizer" "lambda_gw_auth" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${terraform.workspace}-lambda-gw-authorizer"

  jwt_configuration {
    audience = [aws_apigatewayv2_stage.lambda_gw_stage.invoke_url]
    issuer   = "https://${aws_cognito_user_pool.lambda_gw_pool.endpoint}"
  }
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda_gw.name}"
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


resource "aws_apigatewayv2_route" "sdk_upload" {
  api_id    = aws_apigatewayv2_api.lambda_gw.id
  route_key = "POST /sdk_upload"

  target = "integrations/${aws_apigatewayv2_integration.sdk_upload_integration.id}"

  authorizer_id      = aws_apigatewayv2_authorizer.lambda_gw_auth.id
  authorization_type = "JWT"
}

resource "aws_apigatewayv2_integration" "sdk_upload_integration" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "SDK Upload Integration"
  integration_method   = "POST"
  integration_uri      = var.sdk_upload_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_lambda_permission" "sdk_upload_lambda_permission" {
  statement_id  = "AllowSDKUploadAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${terraform.workspace}-${var.sdk_upload_function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway.
  source_arn = "${aws_apigatewayv2_api.lambda_gw.execution_arn}/*/*/*"
}


resource "aws_apigatewayv2_route" "get_sdk_status" {
  api_id    = aws_apigatewayv2_api.lambda_gw.id
  route_key = "POST /get_sdk_status"

  target = "integrations/${aws_apigatewayv2_integration.get_sdk_status_integration.id}"
}

resource "aws_apigatewayv2_integration" "get_sdk_status_integration" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "Get SDK Status Integration"
  integration_method   = "POST"
  integration_uri      = var.get_sdk_status_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_lambda_permission" "sdk_status_lambda_permission" {
  statement_id  = "AllowSDKStatusAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${terraform.workspace}-${var.get_sdk_status_function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway.
  source_arn = "${aws_apigatewayv2_api.lambda_gw.execution_arn}/*/*/*"
}


resource "aws_apigatewayv2_route" "get_auth" {
  api_id    = aws_apigatewayv2_api.lambda_gw.id
  route_key = "POST /get_auth"

  target = "integrations/${aws_apigatewayv2_integration.get_auth_integration.id}"
}

resource "aws_apigatewayv2_integration" "get_auth_integration" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "Get auth integration"
  integration_method   = "POST"
  integration_uri      = var.get_auth_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_lambda_permission" "get_auth_lambda_permission" {
  statement_id  = "AllowGetAuthAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${terraform.workspace}-${var.get_auth_function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway.
  source_arn = "${aws_apigatewayv2_api.lambda_gw.execution_arn}/*/*/*"
}
