output "hash" {
  description = "Docker image source hash"
  value       = data.external.hash.result["hash"]
}

output "ecr_repository_url" {
  description = "ecr repository url"
  value       = aws_ecr_repository.ecr.repository_url
}
