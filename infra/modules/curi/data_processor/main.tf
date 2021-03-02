resource "aws_s3_bucket" "b" {
  bucket = "foo-test-data-bucket"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

module "lambda_function_container_image" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${terraform.workspace}-hello-world-lambda"
  description   = "Hello world lambda"

  create_package = false

  image_uri    = "${var.ecr_repository_url}:2021-03-01"
  package_type = "Image"
}

