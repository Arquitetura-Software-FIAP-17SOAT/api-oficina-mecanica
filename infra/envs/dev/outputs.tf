output "environment" {
  description = "Ambiente provisionado"
  value       = var.environment
}

output "clusterName" {
  description = "Nome do cluster kind"
  value       = module.cluster.clusterName
}

output "kubeconfig" {
  description = "Kubeconfig do cluster (terraform output -raw kubeconfig)"
  value       = module.cluster.kubeconfig
  sensitive   = true
}

output "databaseHost" {
  description = "Host do Postgres dentro do cluster"
  value       = module.database.host
}

output "databaseUrl" {
  description = "DATABASE_URL da API (terraform output -raw databaseUrl)"
  value       = module.database.databaseUrl
  sensitive   = true
}

output "apiUrl" {
  description = "URL no localhost encaminhada para o NodePort apiNodePort do cluster"
  value       = "http://localhost:${var.apiHostPort}"
}
