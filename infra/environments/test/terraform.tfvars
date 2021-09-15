role_arn = "arn:aws:iam::077346344852:role/terraform_deploy_role"

# lambda
image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda2"

# cloud sdk
upload_bucket            = "sdk-upload"
analyzed_bucket          = "sdk-analyzed"
sdk_upload_image_name    = "sdk_upload"
sdk_upload_function_name = "sdk-upload-lambda"

# upload/analysis status
get_sdk_status_image_name    = "get_sdk_status"
get_sdk_status_function_name = "get-sdk-status"

# downloads/dns
hosted_zone = "curibio-test.com"

# squarespace dns
sqsp_verification = "e2xgjnsckpkc3lh9jx52"
