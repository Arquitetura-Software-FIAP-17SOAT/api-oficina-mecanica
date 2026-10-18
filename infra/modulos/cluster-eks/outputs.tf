output "clusterName" {
  description = "Nome do cluster"
  value       = aws_eks_cluster.this.name
}

output "endpoint" {
  description = "Endpoint da API do Kubernetes"
  value       = aws_eks_cluster.this.endpoint
}

output "clusterCaCertificate" {
  description = "Certificado da CA do cluster (base64)"
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "clusterSecurityGroupId" {
  description = "Security group criado pelo EKS e usado pelos nós; libera o acesso ao banco"
  value       = aws_eks_cluster.this.vpc_config[0].cluster_security_group_id
}
