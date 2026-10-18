data "aws_caller_identity" "current" {}

# A AWS Academy não permite criar roles IAM: cluster e nós usam a LabRole existente
data "aws_iam_role" "labrole" {
  name = "LabRole"
}

data "aws_vpc" "vpc" {
  default = true
}

data "aws_subnets" "subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }
}

data "aws_subnet" "subnet" {
  for_each = toset(data.aws_subnets.subnets.ids)
  id       = each.value
}
