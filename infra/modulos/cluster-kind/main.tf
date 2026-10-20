terraform {
  required_providers {
    kind = {
      source = "tehcyx/kind"
    }
  }
}

resource "kind_cluster" "this" {
  name           = var.clusterName
  node_image     = var.nodeImage
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      # Expõe NodePorts do cluster no localhost da máquina
      dynamic "extra_port_mappings" {
        for_each = var.portMappings

        content {
          container_port = extra_port_mappings.value.containerPort
          host_port      = extra_port_mappings.value.hostPort
        }
      }
    }

    dynamic "node" {
      for_each = range(var.workerNodes)

      content {
        role = "worker"
      }
    }
  }
}
