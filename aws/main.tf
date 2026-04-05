data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name_prefix              = "${var.project_name}-${var.environment}"
  api_public_url           = "http://${aws_lb.main.dns_name}:8000"
  default_cors_origins     = "http://localhost:3000,http://127.0.0.1:3000"
  effective_cors_origins   = "${local.default_cors_origins}"
  api_database_url         = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
  api_container_name       = "${local.name_prefix}-api"
  api_log_group_name       = "/ecs/${local.name_prefix}/api"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    CostProfile = "tcc-low-cost"
  }
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(local.tags, { Name = "${local.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "${local.name_prefix}-igw" })
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = merge(
    local.tags,
    {
      Name = "${local.name_prefix}-public-${count.index + 1}"
    }
  )
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = merge(
    local.tags,
    {
      Name = "${local.name_prefix}-private-${count.index + 1}"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.tags, { Name = "${local.name_prefix}-public-rt" })
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = merge(local.tags, { Name = "${local.name_prefix}-private-rt" })
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for the shared load balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${local.name_prefix}-alb-sg" })
}


resource "aws_security_group" "api_service" {
  name        = "${local.name_prefix}-api-service-sg"
  description = "Security group for the api ECS service"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${local.name_prefix}-api-service-sg" })
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Security group for PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api_service.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, { Name = "${local.name_prefix}-db-sg" })
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  tags       = merge(local.tags, { Name = "${local.name_prefix}-db-subnet-group" })
}

resource "aws_db_instance" "postgres" {
  identifier             = "${local.name_prefix}-postgres"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.8"
  instance_class         = "db.t4g.micro"
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false
  multi_az               = false
  tags                   = merge(local.tags, { Name = "${local.name_prefix}-postgres" })
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}


resource "aws_cloudwatch_log_group" "api" {
  name              = local.api_log_group_name
  retention_in_days = 14
  tags              = local.tags
}


data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name_prefix}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.name_prefix}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
  tags               = local.tags
}

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"
  tags = local.tags
}

resource "aws_lb" "main" {
  name               = substr("${local.name_prefix}-alb", 0, 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  tags               = local.tags
}


resource "aws_lb_target_group" "api" {
  name        = substr("${local.name_prefix}-api-tg", 0, 32)
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200-399"
  }

  tags = local.tags
}


resource "aws_lb_listener" "api" {
  load_balancer_arn = aws_lb.main.arn
  port              = 8000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name_prefix}-api"
  cpu                      = tostring(var.api_cpu)
  memory                   = tostring(var.api_memory)
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = local.api_container_name
      image     = "${aws_ecr_repository.api.repository_url}:${var.api_image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = local.api_database_url
        },
        {
          name  = "SECRET_KEY"
          value = var.secret_key
        },
        {
          name  = "CORS_ORIGINS"
          value = local.effective_cors_origins
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = local.tags
}



resource "aws_ecs_service" "api" {
  name            = "${local.name_prefix}-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = true
    security_groups  = [aws_security_group.api_service.id]
    subnets          = aws_subnet.public[*].id
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = local.api_container_name
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.api]

  tags = local.tags
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${local.name_prefix}-frontend-bucket"
  acl    = "private"

  tags = local.tags
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend.iam_arn
        }
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

resource "aws_cloudfront_origin_access_identity" "frontend" {
  comment = "OAI for ${local.name_prefix} frontend CloudFront distribution"
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "${local.name_prefix}-frontend-s3-origin"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix} frontend distribution"
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "${local.name_prefix}-frontend-s3-origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400 # 1 day
    max_ttl                = 31536000 # 1 year
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = local.tags
}


