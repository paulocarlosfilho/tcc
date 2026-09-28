output "frontend_url" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

output "api_url" {
  value = "http://${aws_lb.main.dns_name}:8000"
}

output "api_ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "api_service_name" {
  value = aws_ecs_service.api.name
}

output "database_endpoint" {
  value = aws_db_instance.postgres.address
}
