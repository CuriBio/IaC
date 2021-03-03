provider "aws" {
  region = "us-east-1"
  assume_role {
    role_arn     = "arn:aws:iam::077346344852:role/terraform_deploy_role"
    session_name = "terraform"
  }
}

terraform {
  required_version = ">= 0.14.7"
  backend "s3" {}
}

module "ecr_image" {
  source  = "../../../modules/aws/ecr_image_build_push"
  image_name = "${terraform.workspace}_hello_world"
  image_src = "../../../../src/lambdas/hello_world"
  role_arn     = "arn:aws:iam::077346344852:role/terraform_deploy_role"
}

module "data_processor" {
  depends_on = [module.ecr_image]
  source                = "../../../modules/curi/data_processor"
  data_processor_bucket = "${terraform.workspace}-curi-test-data"
  ecr_repository_url    = module.ecr_image.ecr_repository_url
}
