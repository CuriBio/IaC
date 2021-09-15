output "rds_cluster_port" {
  description = "The port"
  value       = module.rds.rds_cluster_port
}

output "rds_cluster_instance_endpoints" {
  description = "A list of all cluster instance endpoints"
  value       = module.rds.rds_cluster_instance_endpoints
}
