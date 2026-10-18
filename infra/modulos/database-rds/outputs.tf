output "host" {
  description = "Host do banco"
  value       = aws_db_instance.this.address
}

output "port" {
  description = "Porta do banco"
  value       = aws_db_instance.this.port
}

output "databaseUrl" {
  description = "URL de conexão no formato lido pela API (DATABASE_URL)"
  value       = "postgresql://${var.username}:${var.password}@${aws_db_instance.this.address}:${aws_db_instance.this.port}/${var.databaseName}"
  sensitive   = true
}
