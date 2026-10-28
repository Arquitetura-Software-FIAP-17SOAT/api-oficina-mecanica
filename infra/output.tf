output "state_bucket_name" {
  description = "Bucket criado para futura migracao do estado; o backend atual permanece local."
  value       = aws_s3_bucket.bucket-backend.id
}

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