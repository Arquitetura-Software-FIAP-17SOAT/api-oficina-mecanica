locals {
  name = "${var.projectName}-${var.environment}"

  subnetIds = [
    for subnet in data.aws_subnet.subnet : subnet.id
    if !contains(var.unsupportedAvailabilityZones, subnet.availability_zone)
  ]

  tags = {
    project     = var.projectName
    environment = var.environment
    managedBy   = "terraform"
  }
}
