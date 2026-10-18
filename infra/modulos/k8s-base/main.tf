resource "kubernetes_namespace_v1" "this" {
  metadata {
    name = var.namespace

    labels = {
      environment = var.environment
    }
  }
}

# Fornece as métricas de CPU/memória que o HPA usa para escalar
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = var.metricsServerVersion
  namespace  = "kube-system"

  values = [yamlencode({
    args = var.metricsServerInsecureTls ? ["--kubelet-insecure-tls"] : []
  })]
}

# Contrato com os manifests em /k8s: o Deployment da API lê DATABASE_URL deste Secret
resource "kubernetes_secret_v1" "database" {
  metadata {
    name      = var.databaseSecretName
    namespace = kubernetes_namespace_v1.this.metadata[0].name
  }

  data = {
    DATABASE_URL = var.databaseUrl
  }
}
