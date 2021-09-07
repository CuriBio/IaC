output "hash" {
  description = "Docker image source hash"
  value       = data.external.hash.result["hash"]
}

output "ecr_repository_url" {
  description = "ecr repository url"
  value       = aws_ecr_repository.ecr.repository_url
}

output "function_arn" {
  description = "lambda function arn"
  value       = module.lambda_function_container_image.lambda_function_arn
}
