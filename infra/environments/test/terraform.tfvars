role_arn = "arn:aws:iam::077346344852:role/terraform_deploy_role"

# lambda
image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda2"

# cloud sdk
logs_bucket             = "mantarray-logs"
upload_bucket           = "sdk-upload"
analyzed_bucket         = "sdk-analyzed"
s3_upload_image_name    = "s3_upload"
s3_upload_function_name = "s3-upload-lambda"

# upload/analysis status
get_sdk_status_image_name    = "get_sdk_status"
get_sdk_status_function_name = "get-sdk-status"

# auth
get_auth_image_name    = "get_auth"
get_auth_function_name = "get-auth"

# downloads/dns
hosted_zone = "curibio-test.com"

# squarespace dns
sqsp_verification = "e2xgjnsckpkc3lh9jx52"

#database
instance_class = "db.t3.small"
db_creds_arn   = "arn:aws:secretsmanager:us-east-1:077346344852:secret:db-creds-WszNCl"

#jump host
jump_ec2_arn = "arn:aws:secretsmanager:us-east-1:077346344852:secret:db-ec2-key-pair-aofYm8"
jump_host    = "ec2-user@jump.curibio-test.com"
#jump_host    = "ec2-user@ec2-54-226-191-183.compute-1.amazonaws.com"

# firmware updating
main_firmware_bucket              = "main-firmware-bucket"
channel_firmware_bucket           = "channel-firmware-bucket"
get_latest_firmware_image_name    = "get_latest_firmware"
get_latest_firmware_function_name = "get-latest-firmware"
firmware_download_image_name      = "firmware_download"
firmware_download_function_name   = "firmware-download"
