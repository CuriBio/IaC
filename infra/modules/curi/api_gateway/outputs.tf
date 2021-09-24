output "base_url" {
  description = "Base URL for API Gateway stage."
  value       = aws_apigatewayv2_stage.lambda_gw_stage.invoke_url
}

output "cognito_pool_client_id" {
  description = "Client ID of cognito user pool"
  value       = aws_cognito_user_pool_client.lambda_gw_pool_client.id
}
