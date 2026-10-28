data "aws_iam_user" "principal_user" {
  user_name = "11-soat-tf"
}

data "aws_iam_role" "console_role" {
  name = var.console_role_name
}