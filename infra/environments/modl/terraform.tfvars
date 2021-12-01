role_arn = "arn:aws:iam::725604423866:role/terraform_deploy_role"

image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

# cloud sdk
upload_bucket            = "sdk-upload"
analyzed_bucket          = "sdk-analyzed"
sdk_upload_image_name    = "sdk_upload"
sdk_upload_function_name = "sdk-upload-lambda"

# upload/analysis status
get_sdk_status_image_name    = "get_sdk_status"
get_sdk_status_function_name = "get-sdk-status"

# auth
get_auth_image_name    = "get_auth"
get_auth_function_name = "get-auth"

# downloads/dns
hosted_zone = "curibio-modl.com"

# squarespace dns
sqsp_verification = "862laeb5r7tfnxngc2mc"

#database
instance_class = "db.t3.small"
db_creds_arn   = "arn:aws:secretsmanager:us-east-1:725604423866:secret:db-creds-jjqva5"

#jump host
jump_ec2_arn = "arn:aws:secretsmanager:us-east-1:725604423866:secret:db-ec2-key-pair-D29xQo"
jump_host    = "ec2-user@jump.curibio-modl.com"

# firmware updating
main_firmware_bucket              = "main-firmware-bucket"
channel_firmware_bucket           = "channel-firmware-bucket"
get_latest_firmware_image_name    = "get_latest_firmware"
get_latest_firmware_function_name = "get-latest-firmware"
firmware_download_image_name      = "firmware_download"
firmware_download_function_name   = "firmware-download"
