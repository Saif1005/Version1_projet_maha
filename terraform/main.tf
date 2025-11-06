# Configuration Terraform pour FL Crew Reddit sur AWS
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configurer ces valeurs selon votre setup
    # bucket = "your-terraform-state-bucket"
    # key    = "fl-crew-reddit/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "FL-Crew-Reddit"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "Région AWS"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environnement (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Nom du projet"
  type        = string
  default     = "fl-crew-reddit"
}

variable "s3_bucket_name" {
  description = "Nom du bucket S3 pour les données et modèles"
  type        = string
}

variable "ec2_instance_type" {
  description = "Type d'instance EC2 (avec GPU)"
  type        = string
  default     = "g4dn.xlarge"
}

variable "ecs_cluster_name" {
  description = "Nom du cluster ECS"
  type        = string
  default     = "fl-crew-reddit-cluster"
}

# S3 Bucket pour les données et modèles
resource "aws_s3_bucket" "fl_crew_data" {
  bucket = var.s3_bucket_name
  
  tags = {
    Name        = "${var.project_name}-data"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "fl_crew_data" {
  bucket = aws_s3_bucket.fl_crew_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fl_crew_data" {
  bucket = aws_s3_bucket.fl_crew_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM Role pour ECS Tasks
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_s3_access" {
  name = "${var.project_name}-s3-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.fl_crew_data.arn,
          "${aws_s3_bucket.fl_crew_data.arn}/*"
        ]
      }
    ]
  })
}

# ECR Repository pour les images Docker
resource "aws_ecr_repository" "fl_crew_repo" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "fl_crew_cluster" {
  name = var.ecs_cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "fl_crew_task" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "4096"  # 4 vCPU
  memory                   = "8192"  # 8 GB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "${var.project_name}-container"
      image = "${aws_ecr_repository.fl_crew_repo.repository_url}:latest"
      
      environment = [
        {
          name  = "USE_S3_STORAGE"
          value = "true"
        },
        {
          name  = "AWS_S3_BUCKET"
          value = aws_s3_bucket.fl_crew_data.id
        },
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        }
      ]
      
      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.openai_key.arn
        },
        {
          name      = "REDDIT_CLIENT_ID"
          valueFrom = aws_secretsmanager_secret.reddit_client_id.arn
        },
        {
          name      = "REDDIT_CLIENT_SECRET"
          valueFrom = aws_secretsmanager_secret.reddit_client_secret.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fl_crew_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      gpu = [
        {
          count = 1
          type  = "nvidia"
        }
      ]
    }
  ])
}

# IAM Role pour ECS Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Secrets Manager pour les credentials
resource "aws_secretsmanager_secret" "openai_key" {
  name = "${var.project_name}/openai-api-key"
}

resource "aws_secretsmanager_secret" "reddit_client_id" {
  name = "${var.project_name}/reddit-client-id"
}

resource "aws_secretsmanager_secret" "reddit_client_secret" {
  name = "${var.project_name}/reddit-client-secret"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "fl_crew_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 30
}

# VPC et Networking (optionnel, pour ECS Fargate)
resource "aws_vpc" "fl_crew_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "fl_crew_subnet" {
  vpc_id            = aws_vpc.fl_crew_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-subnet"
  }
}

resource "aws_internet_gateway" "fl_crew_igw" {
  vpc_id = aws_vpc.fl_crew_vpc.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_route_table" "fl_crew_rt" {
  vpc_id = aws_vpc.fl_crew_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.fl_crew_igw.id
  }

  tags = {
    Name = "${var.project_name}-rt"
  }
}

resource "aws_route_table_association" "fl_crew_rta" {
  subnet_id      = aws_subnet.fl_crew_subnet.id
  route_table_id = aws_route_table.fl_crew_rt.id
}

# Outputs
output "s3_bucket_name" {
  value = aws_s3_bucket.fl_crew_data.id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.fl_crew_repo.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.fl_crew_cluster.name
}

output "ecs_task_definition_arn" {
  value = aws_ecs_task_definition.fl_crew_task.arn
}

