resource "aws_eks_access_entry" "access_entry" {
  cluster_name      = aws_eks_cluster.cluster.name
  principal_arn     = var.admin_principal_arn != "" ? var.admin_principal_arn : data.aws_caller_identity.current.arn
  kubernetes_groups = ["group-11soat", "group-oficina"]
  type              = "STANDARD"
}

resource "aws_eks_access_policy_association" "access_entry_association" {
  cluster_name  = aws_eks_cluster.cluster.name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  principal_arn = aws_eks_access_entry.access_entry.principal_arn

  access_scope {
    type = "cluster"
  }
}

resource "aws_eks_access_entry" "console_access_entry" {
  count         = var.console_role_name == "" ? 0 : 1
  cluster_name  = aws_eks_cluster.cluster.name
  principal_arn = data.aws_iam_role.console_role[0].arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "console_access_entry_association" {
  count         = var.console_role_name == "" ? 0 : 1
  cluster_name  = aws_eks_cluster.cluster.name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  principal_arn = aws_eks_access_entry.console_access_entry[0].principal_arn

  access_scope {
    type = "cluster"
  }
}

moved {
  from = aws_eks_access_entry.console_access_entry
  to   = aws_eks_access_entry.console_access_entry[0]
}

moved {
  from = aws_eks_access_policy_association.console_access_entry_association
  to   = aws_eks_access_policy_association.console_access_entry_association[0]
}

resource "aws_eks_access_entry" "ci" {
  count         = var.ci_principal_arn == "" ? 0 : 1
  cluster_name  = aws_eks_cluster.cluster.name
  principal_arn = var.ci_principal_arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "ci" {
  count         = var.ci_principal_arn == "" ? 0 : 1
  cluster_name  = aws_eks_cluster.cluster.name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"
  principal_arn = aws_eks_access_entry.ci[0].principal_arn

  access_scope {
    type       = "namespaces"
    namespaces = ["oficina"]
  }
}
