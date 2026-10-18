variable "clusterName" {
  description = "Nome do cluster kind"
  type        = string
}

variable "nodeImage" {
  description = "Imagem dos nós (kindest/node:<versão>). null usa a versão padrão do provider"
  type        = string
  default     = null
}

variable "workerNodes" {
  description = "Quantidade de nós worker além do control-plane"
  type        = number
  default     = 1

  validation {
    condition     = var.workerNodes >= 0 && var.workerNodes <= 3
    error_message = "workerNodes deve estar entre 0 e 3."
  }
}

variable "portMappings" {
  description = "Portas do nó control-plane publicadas no host (containerPort = NodePort do Service)"
  type = list(object({
    containerPort = number
    hostPort      = number
  }))
  default = []
}
