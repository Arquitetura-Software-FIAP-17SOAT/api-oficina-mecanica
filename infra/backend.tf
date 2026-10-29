terraform {
  # O bucket nao aceita variavel aqui: informe no init com
  # terraform init -backend-config="bucket=terraform-oficina-<account_id>"
  backend "s3" {
    key          = "files/terraform.tfstate"
    region       = "us-east-2"
    use_lockfile = true
  }
}