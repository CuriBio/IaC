resource "aws_apigatewayv2_api" "example" {
  name          = "${terraform.workspace}-example"
  protocol_type = "HTTP"
}

# resource "aws_apigatewayv2_authorizer" "example" {
#   api_id           = aws_apigatewayv2_api.example.id
#   authorizer_type  = "JWT"
#   identity_sources = ["$request.header.Authorization"]
#   name             = "example-authorizer"

#   jwt_configuration {
#     audience = ["example"]
#     issuer   = "https://${aws_cognito_user_pool.example.endpoint}"
#   }
# }


resource "aws_cloudwatch_log_group" "api_gw" {
  name = "${terraform.workspace}/aws/api_gw/${aws_apigatewayv2_api.example.name}"
  tags = {
    Environment = terraform.workspace
    Application = "api-gw"
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "${terraform.workspace}-iam_for_lambda"

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

resource "aws_apigatewayv2_integration" "example" {
  api_id           = aws_apigatewayv2_api.example.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "Lambda example"
  integration_method   = "POST"
  integration_uri      = var.sdk_upload_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_route" "example" {
  api_id    = aws_apigatewayv2_api.example.id
  route_key = "POST /example/{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.example.id}"
}

resource "aws_apigatewayv2_stage" "example" {
  api_id      = aws_apigatewayv2_api.example.id
  name        = "${terraform.workspace}-example-stage"
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
