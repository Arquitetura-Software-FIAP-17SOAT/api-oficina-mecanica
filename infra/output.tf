output "vpc_cidr" {
  value = aws_vpc.vpc_fiap.cidr_block
}

output "vpc_id" {
  value = aws_vpc.vpc_fiap.id
}

output "subnet_cidr" {
  value = aws_subnet.subnet_public[0].cidr_block
}

output "subnet_id" {
  value = aws_subnet.subnet_public[0].id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.ecr_repository.repository_url
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}