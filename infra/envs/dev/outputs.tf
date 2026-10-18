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

output "namespace" {
  description = "Namespace da aplicação"
  value       = module.k8s_base.namespace
}

output "databaseHost" {
  description = "Host do Postgres dentro do cluster"
  value       = module.database.host
}

output "databaseSecretName" {
  description = "Secret com a DATABASE_URL para o Deployment da API"
  value       = module.k8s_base.databaseSecretName
}

output "apiUrl" {
  description = "URL da API no localhost (requer Service NodePort na porta apiNodePort)"
  value       = "http://localhost:${var.apiHostPort}"
}

output "loadImageCommand" {
  description = "Comando para carregar a imagem da API no cluster"
  value       = "kind load docker-image <imagem>:<tag> --name ${module.cluster.clusterName}"
}
