# Variables Terraform pour FL Crew Reddit

variable "aws_region" {
  description = "Région AWS pour déployer les ressources"
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
  description = "Nom du bucket S3 (doit être unique globalement)"
  type        = string
}

variable "ec2_instance_type" {
  description = "Type d'instance EC2 avec GPU"
  type        = string
  default     = "g4dn.xlarge"
}

variable "ecs_cluster_name" {
  description = "Nom du cluster ECS"
  type        = string
  default     = "fl-crew-reddit-cluster"
}

variable "ecs_service_name" {
  description = "Nom du service ECS"
  type        = string
  default     = "fl-crew-reddit-service"
}

variable "cpu_units" {
  description = "Unités CPU pour ECS task (1024 = 1 vCPU)"
  type        = number
  default     = 4096
}

variable "memory_mb" {
  description = "Mémoire en MB pour ECS task"
  type        = number
  default     = 8192
}

variable "desired_count" {
  description = "Nombre de tâches ECS désirées"
  type        = number
  default     = 1
}

