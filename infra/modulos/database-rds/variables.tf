variable "identifier" {
  description = "Identificador da instância RDS"
  type        = string
}

variable "vpcId" {
  description = "VPC do banco"
  type        = string
}

variable "subnetIds" {
  description = "Subnets do DB subnet group (no mínimo duas AZs)"
  type        = list(string)
}

variable "allowedSecurityGroupIds" {
  description = "Security groups autorizados a conectar na porta 5432"
  type        = list(string)
}

variable "engineVersion" {
  description = "Versão do PostgreSQL (mesma major do docker-compose)"
  type        = string
  default     = "16"
}

variable "instanceClass" {
  description = "Classe da instância"
  type        = string
  default     = "db.t3.micro"

  validation {
    condition     = contains(["db.t3.micro", "db.t3.small"], var.instanceClass)
    error_message = "Classe invalida, escolha entre db.t3.micro ou db.t3.small."
  }
}

variable "allocatedStorage" {
  description = "Armazenamento em GB"
  type        = number
  default     = 20
}

variable "databaseName" {
  description = "Nome do banco"
  type        = string
}

variable "username" {
  description = "Usuário master do banco"
  type        = string
}

variable "password" {
  description = "Senha do usuário master"
  type        = string
  sensitive   = true
}

variable "skipFinalSnapshot" {
  description = "Não gerar snapshot ao destruir (ambiente acadêmico)"
  type        = bool
  default     = true
}
