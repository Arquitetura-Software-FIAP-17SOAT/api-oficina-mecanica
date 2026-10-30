variable "projectName" {
  type    = string
  default = "oficina"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*[a-z0-9]$", var.projectName))
    error_message = "Use pelo menos dois caracteres: letras minusculas, numeros e hifens; inicie com letra e termine com letra ou numero."
  }
}

variable "region_default" {
  default = "us-east-2"
}

variable "cidr_vpc" {
  default = "10.0.0.0/16"
}

variable "tags" {
  description = "Tags padrao de todos os recursos AWS"
  type        = map(string)
  default     = {}
}

variable "console_role_name" {
  description = "Role IAM do Console AWS que deve enxergar o cluster. Deixe vazio para nao criar o acesso. Exemplo: AccountFullAccessRole"
  type        = string
  default     = ""
}

variable "admin_principal_arn" {
  description = "ARN do usuario/role IAM administrador do EKS. Vazio = quem executa o Terraform (se usar role assumida, informe o ARN da role IAM)"
  type        = string
  default     = ""
}

variable "ci_principal_arn" {
  description = "ARN do usuario IAM usado pelo pipeline (GitHub Actions) para fazer deploy no namespace oficina. Vazio = nao cria o acesso"
  type        = string
  default     = ""
}

variable "instance_type" {
  type    = string
  default = "c7i-flex.large"
}

variable "db_name" {
  default = "oficina"
}

variable "db_username" {
  default = "postgres"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_instance_class" {
  default = "db.t3.micro"
}