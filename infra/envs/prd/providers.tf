terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }

  # O bucket é informado no init: terraform init -backend-config="bucket=<nome-do-bucket>"
  backend "s3" {
    key          = "prd/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.regionDefault

  default_tags {
    tags = local.tags
  }
}
