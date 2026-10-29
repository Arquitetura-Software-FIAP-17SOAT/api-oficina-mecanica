data "aws_caller_identity" "current" {}

data "aws_iam_role" "console_role" {
  count = var.console_role_name == "" ? 0 : 1
  name  = var.console_role_name
}