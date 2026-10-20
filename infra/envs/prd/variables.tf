variable "projectName" {
  description = "Nome do projeto, usado como prefixo dos recursos"
  type        = string
  default     = "oficina"
}

variable "environment" {
  description = "Ambiente (equivale ao APP_ENV)"
  type        = string
  default     = "prd"

  validation {
    condition     = var.environment == "prd"
    error_message = "Este diretório provisiona apenas o ambiente prd."
  }
}

variable "regionDefault" {
  description = "Região usada para criação"
  type        = string
  default     = "us-east-1"
}

variable "unsupportedAvailabilityZones" {
  description = "AZs da VPC default sem suporte ao control plane do EKS"
  type        = list(string)
  default     = ["us-east-1e"]
}

variable "roleName" {
  description = "Role IAM de quem executa o Terraform/kubectl; recebe admin no cluster (voclabs na AWS Academy)"
  type        = string
  default     = "voclabs"
}

variable "instanceTypes" {
  description = "Tipos de instância do node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "nodeDesiredSize" {
  description = "Quantidade desejada de nós"
  type        = number
  default     = 1
}

variable "nodeMaxSize" {
  description = "Quantidade máxima de nós"
  type        = number
  default     = 2
}

variable "databaseInstanceClass" {
  description = "Classe da instância RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "databaseName" {
  description = "Nome do banco"
  type        = string
  default     = "oficina"
}

variable "databaseUsername" {
  description = "Usuário master do banco"
  type        = string
  default     = "oficina"
}
