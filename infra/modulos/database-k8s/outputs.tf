output "host" {
  description = "Host do banco dentro do cluster"
  value       = "${kubernetes_service_v1.this.metadata[0].name}.${var.namespace}.svc.cluster.local"
}

output "port" {
  description = "Porta do banco"
  value       = 5432
}

output "databaseUrl" {
  description = "URL de conexão no formato lido pela API (DATABASE_URL)"
  value       = "postgresql://${var.username}:${var.password}@${kubernetes_service_v1.this.metadata[0].name}.${var.namespace}.svc.cluster.local:5432/${var.databaseName}"
  sensitive   = true
}
