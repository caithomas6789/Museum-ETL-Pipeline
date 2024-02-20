provider "aws" {
    region = "eu-west-2"
}

resource "aws_security_group" "database-sg" {
  name        = "c9-cai-museum-database-sg"
  description = "Allow inbound Postgres traffic"
  vpc_id      = var.VPC_ID

  ingress {
    description      = "Postgres access"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "museum-db" {
  allocated_storage            = 10
  db_name                      = "museum"
  identifier                   = "c9-cai-museum"
  engine                       = "postgres"
  engine_version               = "15.3"
  instance_class               = "db.t3.micro"
  publicly_accessible          = true
  performance_insights_enabled = false
  skip_final_snapshot          = true
  db_subnet_group_name         = "public_subnet_group"
  vpc_security_group_ids       = [aws_security_group.database-sg.id]
  username                     = var.DB_USERNAME
  password                     = var.DB_PASSWORD
}