role_arn = "arn:aws:iam::725604423866:role/terraform_deploy_role"

image_name    = "hello_world"
data_bucket   = "test-data"
function_name = "hello-lambda"

# downloads/dns
hosted_zone = "curibio-modl.com"

# squarespace dns
sqsp_verification = "862laeb5r7tfnxngc2mc"

# s3 downloads users
s3_download_users = [
  "arn:aws:iam::424924102580:user/s3_test"
]
