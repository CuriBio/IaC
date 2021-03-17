remote_state {
  backend = "s3"
  config = {
    profile = "curi_test"
    bucket  = "curi-test-terraform-state"

    key                      = "${path_relative_to_include()}/terraform.tfstate"
    region                   = "us-east-1"
    encrypt                  = true
    skip_bucket_versioning   = false
    skip_bucket_ssencryption = false
    dynamodb_table           = "terraform-lock-table"
  }
}
