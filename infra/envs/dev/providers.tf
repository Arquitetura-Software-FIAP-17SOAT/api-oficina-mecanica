terraform {
  required_version = ">= 1.10"

  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.9"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.36"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }

  # O cluster dev existe só na máquina de quem aplica, então o state também fica local
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "kind" {}

provider "kubernetes" {
  host                   = module.cluster.endpoint
  cluster_ca_certificate = module.cluster.clusterCaCertificate
  client_certificate     = module.cluster.clientCertificate
  client_key             = module.cluster.clientKey
}

provider "helm" {
  kubernetes = {
    host                   = module.cluster.endpoint
    cluster_ca_certificate = module.cluster.clusterCaCertificate
    client_certificate     = module.cluster.clientCertificate
    client_key             = module.cluster.clientKey
  }
}
