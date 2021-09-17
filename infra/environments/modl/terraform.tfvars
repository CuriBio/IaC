role_arn = "arn:aws:iam::725604423866:role/terraform_deploy_role"

image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

# cloud sdk
upload_bucket            = "sdk-upload"
analyzed_bucket          = "sdk-analyzed"
sdk_upload_image_name    = "sdk_upload"
sdk_upload_function_name = "sdk-upload-lambda"

# downloads/dns
hosted_zone = "curibio-modl.com"

# squarespace dns
sqsp_verification = "862laeb5r7tfnxngc2mc"

#database
instance_type = "db.t3.small"
