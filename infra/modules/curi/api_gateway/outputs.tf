output "base_url" {
  description = "Base URL for API Gateway stage."
  value       = aws_apigatewayv2_stage.lambda_gw_stage.invoke_url
}

output "cognito_pool_client_id" {
  description = "Client ID of cognito user pool"
  value       = aws_cognito_user_pool_client.lambda_gw_pool_client.id
}

output "source_arn" {
  description = "api gateway source arn"
  value       = aws_apigatewayv2_api.lambda_gw.execution_arn
}

output "api_id" {
  description = "api id"
  value       = aws_apigatewayv2_api.lambda_gw.id
}

output "api_stage_id" {
  description = "api stage id"
  value       = aws_apigatewayv2_stage.lambda_gw_stage.id
}

output "authorizer_id" {
  description = "authorizer id"
  value       = aws_apigatewayv2_authorizer.lambda_gw_auth.id
}
