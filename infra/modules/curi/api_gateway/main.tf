resource "aws_apigatewayv2_api" "lambda_gw" {
  name          = "${terraform.workspace}-lambda-gw"
  protocol_type = "HTTP"
}

# resource "aws_apigatewayv2_authorizer" "lambda_gw_auth" {
#   api_id           = aws_apigatewayv2_api.lambda_gw.id
#   authorizer_type  = "JWT"
#   identity_sources = ["$request.header.Authorization"]
#   name             = "${terraform.workspace}-lambda-gw-authorizer"

#   jwt_configuration {
#     audience = ["TODO"]
#     issuer   = "https://${aws_cognito_user_pool.TODO.endpoint}"
#   }
# }

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda_gw.name}"
  tags = {
    Environment = terraform.workspace
    Application = "api-gw"
  }
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowSDKUploadAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${terraform.workspace}-${var.sdk_upload_function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway.
  source_arn = "${aws_apigatewayv2_api.lambda_gw.execution_arn}/*/*/*"
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

resource "aws_apigatewayv2_integration" "sdk_upload_integration" {
  api_id           = aws_apigatewayv2_api.lambda_gw.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "SDK Upload Integration"
  integration_method   = "POST"
  integration_uri      = var.sdk_upload_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_route" "sdk_upload" {
  api_id    = aws_apigatewayv2_api.lambda_gw.id
  route_key = "POST /sdk_upload"

  target = "integrations/${aws_apigatewayv2_integration.sdk_upload_integration.id}"
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
