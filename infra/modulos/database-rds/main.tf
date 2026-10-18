resource "aws_db_subnet_group" "this" {
  name       = var.identifier
  subnet_ids = var.subnetIds
}

resource "aws_security_group" "this" {
  name        = "SG-${var.identifier}-db"
  description = "Acesso ao PostgreSQL ${var.identifier} a partir do cluster"
  vpc_id      = var.vpcId

  ingress {
    description     = "PostgreSQL a partir dos nos do cluster"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowedSecurityGroupIds
  }

  egress {
    description = "All"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "this" {
  identifier     = var.identifier
  engine         = "postgres"
  engine_version = var.engineVersion
  instance_class = var.instanceClass

  allocated_storage = var.allocatedStorage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.databaseName
  username = var.username
  password = var.password

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.this.id]
  publicly_accessible    = false

  apply_immediately   = true
  deletion_protection = false
  skip_final_snapshot = var.skipFinalSnapshot
}
