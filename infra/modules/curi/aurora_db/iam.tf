resource "aws_iam_role" "dbConnectRole" {
  name               = "${terraform.workspace}-db-connect-role"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "rds-db:connect"
        ],
        "Resource": [
            " arn:aws:rds-db:us-east-1:077346344852:dbuser:cluster-CHFYU2HG6ZHXEYTJK5CWZZFRWQ/*"
        ]
    }]
}
  EOF
  tags = {
    Name = "${terraform.workspace}-db-iam-role"
  }
}


resource "aws_iam_role_policy_attachment" "dbconnect_policy" {
  role       = aws_iam_role.dbConnectRole.name
  policy_arn = "arn:aws:rds-db:us-east-1:077346344852:dbuser:cluster-CHFYU2HG6ZHXEYTJK5CWZZFRWQ/*"
}
