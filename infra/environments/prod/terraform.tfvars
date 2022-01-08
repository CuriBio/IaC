role_arn = "arn:aws:iam::245339368379:role/terraform_deploy_role"

# lambda
image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

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
hosted_zone = "curibio.com"

# squarespace dns
sqsp_verification = "a6a6hxwse7f7keb3h845"

#database
instance_class = "db.t3.small"
db_creds_arn   = "arn:aws:secretsmanager:us-east-1:245339368379:secret:db-creds-hdEvmn"

#jump host
jump_ec2_arn = "arn:aws:secretsmanager:us-east-1:245339368379:secret:db-ec2-key-pair-FRSQ2E"
jump_host    = "ec2-user@jump.curibio.com"

# firmware updating
main_firmware_bucket              = "main-firmware-bucket"
channel_firmware_bucket           = "channel-firmware-bucket"
get_latest_firmware_image_name    = "get_latest_firmware"
get_latest_firmware_function_name = "get-latest-firmware"
firmware_download_image_name      = "firmware_download"
firmware_download_function_name   = "firmware-download"
