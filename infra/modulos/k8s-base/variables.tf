variable "namespace" {
  description = "Namespace da aplicação"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev ou prd), usado como label do namespace"
  type        = string
}

variable "metricsServerVersion" {
  description = "Versão do chart do metrics-server"
  type        = string
  default     = "3.12.2"
}

variable "metricsServerInsecureTls" {
  description = "Ignora o certificado autoassinado do kubelet (necessário no kind)"
  type        = bool
  default     = false
}

variable "databaseSecretName" {
  description = "Nome do Secret com a DATABASE_URL consumido pelo Deployment da API"
  type        = string
  default     = "oficina-db"
}

variable "databaseUrl" {
  description = "URL de conexão com o banco"
  type        = string
  sensitive   = true
}
