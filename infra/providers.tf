provider "aws" {
  region = var.region_default

  default_tags {
    tags = var.tags
  }
}