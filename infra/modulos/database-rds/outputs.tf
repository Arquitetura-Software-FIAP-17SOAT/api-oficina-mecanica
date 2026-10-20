output "host" {
  description = "Host do banco"
  value       = aws_db_instance.this.address
}

output "port" {
  description = "Porta do banco"
  value       = aws_db_instance.this.port
}

output "databaseUrl" {
  description = "URL de conexão no formato lido pela API (DATABASE_URL); driver explícito porque o SQLAlchemy 2.1 usa psycopg v3 por padrão"
  value       = "postgresql+psycopg2://${var.username}:${var.password}@${aws_db_instance.this.address}:${aws_db_instance.this.port}/${var.databaseName}"
  sensitive   = true
}
