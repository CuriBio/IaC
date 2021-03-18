role_arn = "arn:aws:iam::245339368379:role/terraform_deploy_role"

image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

# downloads/dns
hosted_zone = "curibio.com"

# squarespace dns
sqsp_verification = "a6a6hxwse7f7keb3h845"

# s3 downloads users
s3_download_users = [
  "arn:aws:iam::424924102580:user/s3_test"
]
