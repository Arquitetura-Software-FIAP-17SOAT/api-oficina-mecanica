module "cluster" {
  source = "../../modulos/cluster-eks"

  clusterName     = local.name
  roleArn         = data.aws_iam_role.labrole.arn
  principalArn    = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.roleName}"
  vpcId           = data.aws_vpc.vpc.id
  vpcCidr         = data.aws_vpc.vpc.cidr_block
  subnetIds       = local.subnetIds
  instanceTypes   = var.instanceTypes
  nodeDesiredSize = var.nodeDesiredSize
  nodeMaxSize     = var.nodeMaxSize
}

resource "random_password" "database" {
  length  = 32
  special = false
}

module "database" {
  source = "../../modulos/database-rds"

  identifier              = local.name
  vpcId                   = data.aws_vpc.vpc.id
  subnetIds               = local.subnetIds
  allowedSecurityGroupIds = [module.cluster.clusterSecurityGroupId]
  instanceClass           = var.databaseInstanceClass
  databaseName            = var.databaseName
  username                = var.databaseUsername
  password                = random_password.database.result
}

# Registry da imagem da API; o CI faz push aqui e o Deployment puxa daqui
resource "aws_ecr_repository" "api" {
  name                 = "${local.name}-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}
