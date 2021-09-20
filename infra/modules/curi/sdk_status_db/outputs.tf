output "db_arn" {
  description = "SDK Status DB arn"
  value       = aws_dynamodb_table.sdk_analysis_statuses.arn
}
