resource "aws_dynamodb_table" "sdk_analysis_statuses" {
  name           = "${terraform.workspace}-sdk-analysis-statuses"
  billing_mode   = "PROVISIONED" # TODO
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "upload_id"

  attribute {
    name = "upload_id"
    type = "S"
  }

  # attribute {
  #   name = "file_name"
  #   type = "S"
  # }

  # attribute {
  #   name = "sdk_status"
  #   type = "S"
  # }
}
