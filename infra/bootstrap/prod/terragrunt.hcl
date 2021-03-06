remote_state {
  backend = "s3"
  config = {
    profile = "curi_prod"
    bucket = "curi-prod-terraform-state"

    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}
