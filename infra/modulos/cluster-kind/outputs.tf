output "clusterName" {
  description = "Nome do cluster"
  value       = kind_cluster.this.name
}

output "endpoint" {
  description = "Endpoint da API do Kubernetes"
  value       = kind_cluster.this.endpoint
}

output "clusterCaCertificate" {
  description = "Certificado da CA do cluster (PEM)"
  value       = kind_cluster.this.cluster_ca_certificate
}

output "clientCertificate" {
  description = "Certificado de cliente do usuário admin (PEM)"
  value       = kind_cluster.this.client_certificate
  sensitive   = true
}

output "clientKey" {
  description = "Chave privada do usuário admin (PEM)"
  value       = kind_cluster.this.client_key
  sensitive   = true
}

output "kubeconfig" {
  description = "Kubeconfig completo do cluster"
  value       = kind_cluster.this.kubeconfig
  sensitive   = true
}
