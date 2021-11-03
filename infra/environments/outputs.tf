output "role_arn" {
  description = "terraform role arn"
  value       = var.role_arn
}

output "db_creds_arn" {
  description = "db credentials arn"
  value       = var.db_creds_arn
}

output "db_name" {
  description = "db name"
  value       = module.aurora_database.db_name
}

output "db_cluster_endpoint" {
  description = "rds writer endpoint"
  value       = module.aurora_database.cluster_endpoint
}

output "jump_ec2_arn" {
  description = "jump_ec2 arn"
  value       = var.jump_ec2_arn
}

output "jump_host" {
  description = "jump host"
  value       = var.jump_host
}
