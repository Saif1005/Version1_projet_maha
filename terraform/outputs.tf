# Outputs Terraform

output "s3_bucket_name" {
  description = "Nom du bucket S3 créé"
  value       = aws_s3_bucket.fl_crew_data.id
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3"
  value       = aws_s3_bucket.fl_crew_data.arn
}

output "ecr_repository_url" {
  description = "URL du repository ECR"
  value       = aws_ecr_repository.fl_crew_repo.repository_url
}

output "ecs_cluster_name" {
  description = "Nom du cluster ECS"
  value       = aws_ecs_cluster.fl_crew_cluster.name
}

output "ecs_cluster_arn" {
  description = "ARN du cluster ECS"
  value       = aws_ecs_cluster.fl_crew_cluster.arn
}

output "ecs_task_definition_arn" {
  description = "ARN de la task definition ECS"
  value       = aws_ecs_task_definition.fl_crew_task.arn
}

output "vpc_id" {
  description = "ID du VPC créé"
  value       = aws_vpc.fl_crew_vpc.id
}

output "subnet_id" {
  description = "ID du subnet créé"
  value       = aws_subnet.fl_crew_subnet.id
}

