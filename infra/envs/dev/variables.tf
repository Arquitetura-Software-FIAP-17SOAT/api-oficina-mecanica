variable "projectName" {
  description = "Nome do projeto, usado como prefixo dos recursos"
  type        = string
  default     = "oficina"
}

variable "environment" {
  description = "Ambiente (equivale ao APP_ENV)"
  type        = string
  default     = "dev"

  validation {
    condition     = var.environment == "dev"
    error_message = "Este diretório provisiona apenas o ambiente dev."
  }
}

variable "namespace" {
  description = "Namespace da aplicação"
  type        = string
  default     = "oficina"
}

variable "workerNodes" {
  description = "Quantidade de nós worker do kind"
  type        = number
  default     = 1
}

variable "apiNodePort" {
  description = "NodePort do Service da API definido nos manifests em /k8s"
  type        = number
  default     = 30080
}

variable "apiHostPort" {
  description = "Porta do localhost que encaminha para o NodePort da API"
  type        = number
  default     = 8080
}

variable "databaseName" {
  description = "Nome do banco"
  type        = string
  default     = "oficina"
}

variable "databaseUsername" {
  description = "Usuário do banco"
  type        = string
  default     = "oficina"
}
