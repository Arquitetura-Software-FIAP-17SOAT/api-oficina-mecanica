output "environment" {
  description = "Ambiente provisionado"
  value       = var.environment
}

output "clusterName" {
  description = "Nome do cluster EKS"
  value       = module.cluster.clusterName
}

output "clusterEndpoint" {
  description = "Endpoint da API do Kubernetes"
  value       = module.cluster.endpoint
}

output "kubeconfigCommand" {
  description = "Comando para configurar o kubectl"
  value       = "aws eks update-kubeconfig --name ${module.cluster.clusterName} --region ${var.regionDefault}"
}

output "namespace" {
  description = "Namespace da aplicação"
  value       = module.k8s_base.namespace
}

output "databaseHost" {
  description = "Endpoint do RDS"
  value       = module.database.host
}

output "databaseSecretName" {
  description = "Secret com a DATABASE_URL para o Deployment da API"
  value       = module.k8s_base.databaseSecretName
}

output "ecrRepositoryUrl" {
  description = "Repositório ECR da imagem da API"
  value       = aws_ecr_repository.api.repository_url
}
