data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "bucket-backend" {
  bucket        = "${var.projectName}-tfstate-${data.aws_caller_identity.current.account_id}-${var.region_default}"
  force_destroy = false

  lifecycle {
    precondition {
      condition     = length("${var.projectName}-tfstate-${data.aws_caller_identity.current.account_id}-${var.region_default}") <= 63
      error_message = "O nome completo do bucket deve ter no maximo 63 caracteres; reduza projectName."
    }
  }
}

resource "aws_s3_bucket_versioning" "backend" {
  bucket = aws_s3_bucket.bucket-backend.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "backend" {
  bucket = aws_s3_bucket.bucket-backend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backend" {
  bucket = aws_s3_bucket.bucket-backend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}