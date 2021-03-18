role_arn = "arn:aws:iam::077346344852:role/terraform_deploy_role"

# lambda
image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda2"

# downloads/dns
hosted_zone = "curibio-test.com"

# squarespace dns
sqsp_verification = "e2xgjnsckpkc3lh9jx52"

# s3 downloads users
s3_download_users = [
  "arn:aws:iam::424924102580:user/s3_test"
]
