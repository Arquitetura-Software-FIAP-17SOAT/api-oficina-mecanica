output "namespace" {
  description = "Namespace da aplicação"
  value       = kubernetes_namespace_v1.this.metadata[0].name
}

output "databaseSecretName" {
  description = "Nome do Secret com a DATABASE_URL"
  value       = kubernetes_secret_v1.database.metadata[0].name
}
