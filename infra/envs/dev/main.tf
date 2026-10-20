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

module "database" {
  source = "../../modulos/database-k8s"

  namespace    = var.databaseNamespace
  databaseName = var.databaseName
  username     = var.databaseUsername
  password     = random_password.database.result
}
