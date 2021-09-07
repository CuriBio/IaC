output "rds_cluster_master_password" {
  description = "aurora database master password"
  value       = module.aurora_db.master_password
}
output "rds_cluster_master_username" {
  description = "aurora database master username"
  value       = module.aurora_db.master_username
}
output "security_group_id" {
  description = "aurora database security group id"
  value       = module.aurora_db.security_group_id
}