output "ecr_repository_url" {
  value = aws_ecr_repository.foo.repository_url
  description = "ECR repository url"
}

output "arn" {
  value = var.role_arn
  description = "role arn"
}
