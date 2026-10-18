resource "aws_security_group" "cluster" {
  name        = "SG-${var.clusterName}"
  description = "Security group adicional do control plane do EKS ${var.clusterName}"
  vpc_id      = var.vpcId

  ingress {
    description = "API do Kubernetes a partir da VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpcCidr]
  }

  egress {
    description = "All"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eks_cluster" "this" {
  name     = var.clusterName
  role_arn = var.roleArn
  version  = var.kubernetesVersion

  vpc_config {
    subnet_ids         = var.subnetIds
    security_group_ids = [aws_security_group.cluster.id]
  }

  access_config {
    authentication_mode = "API_AND_CONFIG_MAP"
    # O acesso de admin é concedido explicitamente pelo access entry abaixo;
    # com o bootstrap ligado, o EKS cria a mesma entrada e o apply falha por duplicidade
    bootstrap_cluster_creator_admin_permissions = false
  }
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "NG-${var.clusterName}"
  node_role_arn   = var.roleArn
  subnet_ids      = var.subnetIds
  disk_size       = var.diskSize
  instance_types  = var.instanceTypes

  scaling_config {
    desired_size = var.nodeDesiredSize
    max_size     = var.nodeMaxSize
    min_size     = var.nodeMinSize
  }

  update_config {
    max_unavailable = 1
  }
}

resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.this.name
  principal_arn = var.principalArn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.this.name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  principal_arn = aws_eks_access_entry.admin.principal_arn

  access_scope {
    type = "cluster"
  }
}
