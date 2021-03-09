remote_state {
  backend = "s3"
  config = {
    bucket = "curi-infrastructure-state"

    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}
