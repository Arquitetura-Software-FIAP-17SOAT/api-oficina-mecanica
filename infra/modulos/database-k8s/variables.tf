variable "namespace" {
  description = "Namespace onde o Postgres roda"
  type        = string
}

variable "name" {
  description = "Nome do StatefulSet e do Service (vira o host do banco)"
  type        = string
  default     = "postgres"
}

variable "image" {
  description = "Imagem do Postgres (mesma do docker-compose)"
  type        = string
  default     = "postgres:16-alpine"
}

variable "databaseName" {
  description = "Nome do banco"
  type        = string
}

variable "username" {
  description = "Usuário do banco"
  type        = string
}

variable "password" {
  description = "Senha do banco"
  type        = string
  sensitive   = true
}

variable "storageSize" {
  description = "Tamanho do volume de dados"
  type        = string
  default     = "1Gi"
}

variable "storageClassName" {
  description = "StorageClass do volume. null usa a classe padrão do cluster"
  type        = string
  default     = null
}
