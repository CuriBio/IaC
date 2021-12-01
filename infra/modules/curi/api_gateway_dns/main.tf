resource "aws_apigatewayv2_domain_name" "lambda_gw_domain_name" {
  domain_name = "${var.subdomain}.${var.hosted_zone}"

  domain_name_configuration {
    certificate_arn = var.ssl_cert_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "lambda_gw_mapping" {
  api_id      = var.lambda_api_gw_id
  domain_name = aws_apigatewayv2_domain_name.lambda_gw_domain_name.id
  stage       = var.lambda_api_stage_id
}
