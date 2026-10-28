terraform {
  backend "s3" {
    bucket = "terraform-oficina"
    key    = "files/terraform.tfstate"
    region = "us-east-2"
  }
}