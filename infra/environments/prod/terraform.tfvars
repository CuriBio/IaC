role_arn = "arn:aws:iam::245339368379:role/terraform_deploy_role"

image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

# cloud sdk
upload_bucket            = "sdk-upload"
analyzed_bucket          = "sdk-analyzed"
sdk_upload_image_name    = "sdk_upload"
sdk_upload_function_name = "sdk-upload-lambda"

# downloads/dns
hosted_zone = "curibio.com"

# squarespace dns
sqsp_verification = "a6a6hxwse7f7keb3h845"

#database
instance_type = "db.t3.small"
db_username   = "admin"
db_password   = "testDBsetup1234"
