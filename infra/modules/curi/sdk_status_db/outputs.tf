output "name" {
  description = "SDK Status table name"
  value       = aws_dynamodb_table.sdk_analysis_statuses.id
}

output "arn" {
  description = "SDK Status table name"
  value       = aws_dynamodb_table.sdk_analysis_statuses.arn
}
