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

variable "instance_type" {
  type    = string
  default = "t3.medium"
}