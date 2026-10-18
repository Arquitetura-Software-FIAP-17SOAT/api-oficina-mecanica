module "cluster" {
  source = "../../modulos/cluster-kind"

  clusterName = local.name
  workerNodes = var.workerNodes

  portMappings = [{
    containerPort = var.apiNodePort
    hostPort      = var.apiHostPort
  }]
}

resource "random_password" "database" {
  length  = 32
  special = false
}

module "k8s_base" {
  source = "../../modulos/k8s-base"

  namespace   = var.namespace
  environment = var.environment
  databaseUrl = module.database.databaseUrl

  # O kubelet do kind usa certificado autoassinado
  metricsServerInsecureTls = true
}

module "database" {
  source = "../../modulos/database-k8s"

  namespace    = module.k8s_base.namespace
  databaseName = var.databaseName
  username     = var.databaseUsername
  password     = random_password.database.result
}
