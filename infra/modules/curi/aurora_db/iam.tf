resource "aws_iam_role" "dbConnectRole" {
  name               = "${terraform.workspace}-db-connect-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
  tags = {
    Name = "${terraform.workspace}-db-iam-role"
  }
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["rds-db:connect"]
    effect  = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:rds-db:us-east-1:077346344852:dbuser:cluster-CHFYU2HG6ZHXEYTJK5CWZZFRWQ/*"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "dbconnect_policy" {
  role       = aws_iam_role.dbConnectRole.name
  policy_arn = "arn:aws:rds-db:us-east-1:077346344852:dbuser:cluster-CHFYU2HG6ZHXEYTJK5CWZZFRWQ/*"
}
