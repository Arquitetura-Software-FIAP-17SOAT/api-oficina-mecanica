resource "aws_db_subnet_group" "rds" {
  name       = "rds-${var.projectName}"
  subnet_ids = aws_subnet.subnet_public[*].id
}

resource "aws_security_group" "rds" {
  name        = "rds-${var.projectName}-sg"
  description = "Permite PostgreSQL apenas a partir do EKS"
  vpc_id      = aws_vpc.vpc_fiap.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_eks_cluster.cluster.vpc_config[0].cluster_security_group_id]
  }
}

resource "aws_db_instance" "postgres" {
  identifier        = "rds-${var.projectName}"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = 1
  skip_final_snapshot     = true
}