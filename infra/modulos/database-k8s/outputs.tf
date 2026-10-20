output "host" {
  description = "Host do banco dentro do cluster"
  value       = "${kubernetes_service_v1.this.metadata[0].name}.${var.namespace}.svc.cluster.local"
}

output "port" {
  description = "Porta do banco"
  value       = 5432
}

output "databaseUrl" {
  description = "URL de conexão no formato lido pela API (DATABASE_URL); driver explícito porque o SQLAlchemy 2.1 usa psycopg v3 por padrão"
  value       = "postgresql+psycopg2://${var.username}:${var.password}@${kubernetes_service_v1.this.metadata[0].name}.${var.namespace}.svc.cluster.local:5432/${var.databaseName}"
  sensitive   = true
}
