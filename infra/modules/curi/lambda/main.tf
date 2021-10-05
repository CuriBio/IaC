# resource "aws_s3_bucket" "b" {
#   bucket = var.data_bucket
#   acl    = "private"

#   server_side_encryption_configuration {
#     rule {
#       apply_server_side_encryption_by_default {
#         sse_algorithm = "AES256"
#       }
#     }
#   }
# }

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
  triggers = {
    hash = data.external.hash.result["hash"]
  }

  provisioner "local-exec" {
    command = "(cd ${var.image_src} && make build)"

    environment = {
      IMAGE = var.image_name
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
      IMAGE    = var.image_name
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
      IMAGE    = var.image_name
      TAG      = "latest"
    }
  }
}

module "lambda_function_container_image" {
  depends_on = [null_resource.docker_push]
  source     = "terraform-aws-modules/lambda/aws"

  function_name         = var.function_name
  description           = var.function_description
  environment_variables = var.lambda_env

  create_package = false

  image_uri    = "${aws_ecr_repository.ecr.repository_url}:latest"
  package_type = "Image"

  allowed_triggers         = var.allowed_triggers
  attach_policy_statements = length(var.attach_policies) > 0
  policy_statements        = var.attach_policies
}


resource "aws_lambda_permission" "lambda_permission" {
  depends_on = [module.lambda_function_container_image]

  statement_id  = "AllowAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway.
  source_arn = "${var.source_arn}/*/*/*"
  #source_arn = "${aws_apigatewayv2_api.lambda_gw.execution_arn}/*/*/*"
}

resource "aws_apigatewayv2_integration" "lambda_api_integration" {
  api_id           = var.lambda_api_gw_id
  #api_id           = aws_apigatewayv2_api.lambda_gw.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = var.function_description
  integration_method   = var.integration_method
  integration_uri      = module.lambda_function_container_image.lambda_function_invoke_arn
  passthrough_behavior = "WHEN_NO_MATCH"
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = var.lambda_api_gw_id
  #"POST /get_auth"
  route_key = var.route_key

  target = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}
