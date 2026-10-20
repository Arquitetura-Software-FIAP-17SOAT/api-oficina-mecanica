variable "clusterName" {
  description = "Nome do cluster EKS"
  type        = string
}

variable "kubernetesVersion" {
  description = "Versão do Kubernetes. null usa a versão padrão do EKS"
  type        = string
  default     = null
}

variable "roleArn" {
  description = "ARN da role usada pelo cluster e pelos nós (LabRole na AWS Academy)"
  type        = string
}

variable "principalArn" {
  description = "ARN da role IAM que recebe acesso de admin ao cluster (kubectl / CI)"
  type        = string
}

variable "vpcId" {
  description = "VPC onde o cluster é criado"
  type        = string
}

variable "vpcCidr" {
  description = "CIDR da VPC, liberado para acessar a API do cluster"
  type        = string
}

variable "subnetIds" {
  description = "Subnets do cluster e do node group (em AZs suportadas pelo EKS)"
  type        = list(string)
}

variable "instanceTypes" {
  description = "Tipos de instância do node group"
  type        = list(string)
  default     = ["t3.medium"]

  validation {
    condition     = alltrue([for type in var.instanceTypes : contains(["t3.medium", "t3.large"], type)])
    error_message = "Tipo de instancia invalido, escolha entre t3.medium ou t3.large."
  }
}

variable "diskSize" {
  description = "Disco de cada nó, em GB"
  type        = number
  default     = 50
}

variable "nodeDesiredSize" {
  description = "Quantidade desejada de nós"
  type        = number
  default     = 1
}

variable "nodeMinSize" {
  description = "Quantidade mínima de nós"
  type        = number
  default     = 1
}

variable "nodeMaxSize" {
  description = "Quantidade máxima de nós"
  type        = number
  default     = 2
}
