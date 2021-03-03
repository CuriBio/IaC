resource "aws_ecr_repository" "ecr" {
  name                 = var.image_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

data "external" "hash" {
  program = ["${path.module}/hash.sh", var.image_src]
}

resource "null_resource" "docker_build" {
  depends_on = [aws_ecr_repository.ecr]

  triggers = {
    hash = data.external.hash.result["hash"]
  }

  provisioner "local-exec" {
    command = "(cd ${var.image_src} && make build tag)"

    environment = {
      ECR_REPO = aws_ecr_repository.ecr.repository_url
      ROLE_ARN = var.role_arn
    }
  }
}

resource "null_resource" "docker_push" {
  depends_on = [null_resource.docker_build]

  provisioner "local-exec" {
    command = "(${path.module}/push.sh)"

    environment = {
      ECR_REPO = aws_ecr_repository.ecr.repository_url
      ROLE_ARN = var.role_arn
      IMAGE    = var.image_name
      TAG      = "latest"
    }
  }
}

