# resource "aws_iam_service_linked_role" "ecs_service_linked_role" {
#   aws_service_name = "ecs.amazonaws.com"
# }

resource "aws_ecr_repository" "ecr" {
  name                 = "${terraform.workspace}-${var.image_name}"
  image_tag_mutability = "MUTABLE"

  # image_scanning_configuration {
  #   scan_on_push = true
  # }
}

data "external" "hash" {
  program = ["${path.module}/hash.sh", var.image_src]
}

resource "null_resource" "docker_build" {
  triggers = {
    hash = data.external.hash.result["hash"]
  }

  provisioner "local-exec" {
    command = "(cd ${var.image_src} && make build)"

    environment = {
      IMAGE = "${terraform.workspace}-${var.image_name}"
      TAG   = "latest"
    }
  }
}

resource "null_resource" "docker_tag" {
  depends_on = [aws_ecr_repository.ecr, null_resource.docker_build]

  triggers = {
    hash = data.external.hash.result["hash"]
  }

  provisioner "local-exec" {
    command = "(cd ${var.image_src} && make tag)"

    environment = {
      ECR_REPO = aws_ecr_repository.ecr.repository_url
      ROLE_ARN = var.role_arn
      IMAGE    = "${terraform.workspace}-${var.image_name}"
      TAG      = "latest"
    }
  }
}

resource "null_resource" "docker_push" {
  depends_on = [null_resource.docker_tag]

  triggers = {
    hash = data.external.hash.result["hash"]
  }

  provisioner "local-exec" {
    command = "(${path.module}/push.sh)"

    environment = {
      ECR_REPO = aws_ecr_repository.ecr.repository_url
      ROLE_ARN = var.role_arn
      IMAGE    = "${terraform.workspace}-${var.image_name}"
      TAG      = "latest"
    }
  }
}

resource "aws_ecs_cluster" "aws-ecs-cluster" {
  name = "${terraform.workspace}-${var.image_name}-cluster"
  tags = {
    Name = "${terraform.workspace}-${var.image_name}-ecs"
  }
}

resource "aws_ecs_task_definition" "aws-ecs-task" {
  family                   = "${terraform.workspace}-${var.image_name}-ecs-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  memory                   = "512"
  cpu                      = "256"
  execution_role_arn       = aws_iam_role.ecsTaskExecutionRole.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  depends_on               = [null_resource.docker_push]
  container_definitions    = <<EOF
[
  {
    "name": "${terraform.workspace}-${var.image_name}",
    "image": "${aws_ecr_repository.ecr.repository_url}:latest",
    "memory": 512,
    "cpu": 256,
    "essential": true,
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "sdk-analysis-service",
        "awslogs-group": "${aws_cloudwatch_log_group.sdk_analysis_logs.name}"
      }
    },
    "environment": ${jsonencode(var.task_env)}
  }
]
EOF
}


resource "aws_cloudwatch_log_group" "sdk_analysis_logs" {
  name = "${terraform.workspace}-sdk-analysis"

  tags = {
    Environment = terraform.workspace
    Application = "sdk-analysis"
  }
}


# Providing a reference to our default VPC
resource "aws_default_vpc" "default_vpc" {
}

# Providing a reference to our default subnets
resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "us-east-1a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "us-east-1b"
}

resource "aws_default_subnet" "default_subnet_c" {
  availability_zone = "us-east-1c"
}

data "aws_ecs_task_definition" "main" {
  task_definition = aws_ecs_task_definition.aws-ecs-task.family
}

resource "aws_ecs_service" "aws-ecs-service" {
  name            = "${terraform.workspace}-${var.image_name}-ecs-service"
  cluster         = aws_ecs_cluster.aws-ecs-cluster.id
  task_definition = aws_ecs_task_definition.aws-ecs-task.arn
  #task_definition      = "${aws_ecs_task_definition.aws-ecs-task.family}:${max(aws_ecs_task_definition.aws-ecs-task.revision, data.aws_ecs_task_definition.main.revision)}"

  launch_type         = "FARGATE"
  scheduling_strategy = "REPLICA"
  desired_count       = 1

  force_new_deployment = true

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200

  network_configuration {
    subnets          = [aws_default_subnet.default_subnet_a.id, aws_default_subnet.default_subnet_b.id, aws_default_subnet.default_subnet_c.id]
    assign_public_ip = true
  }
}
