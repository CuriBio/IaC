resource "aws_iam_role" "terraform_role" {
  name = "terraform_deploy_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          AWS = "arn:aws:iam::${var.account_id}:root"
        }
        Condition = {}
      },
    ]
  })
}

resource "aws_iam_role_policy" "policy" {
  name = "terraform_deploy_policy"
  role = aws_iam_role.terraform_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*",
          "ec2:DescribeAccountAttributes",
          "ecr:*",
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:ListTagsLogGroup",
          "iam:CreateRole",
          "iam:PassRole",
          "iam:CreatePolicy",
          "iam:DeleteRole",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:GetRole",
          "iam:ListInstanceProfilesForRole",
          "iam:ListAttachedRolePolicies",
          "iam:ListRolePolicies",
          "iam:ListPolicyVersions",
          "iam:AttachRolePolicy",
          "iam:ListEntitiesForPolicy",
          "iam:DetachRolePolicy",
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:ListVersionsByFunction",
          "route53:CreateHostedZone",
          "route53:GetChange",
          "route53:GetHostedZone",
          "route53:ListTagsForResource",
          "route53:DeleteHostedZone",
          "route53:ChangeResourceRecordSets",
          "route53:ListResourceRecordSets",
          "cloudfront:CreateDistribution",
          "cloudfront:TagResource",
          "cloudfront:GetDistribution",
          "cloudfront:ListTagsForResource",
          "cloudfront:DeleteDistribution",
          "cloudfront:UpdateDistribution",
          "acm:RequestCertificate",
          "acm:AddTagsToCertificate",
          "acm:DescribeCertificate",
          "acm:ListTagsForCertificate",
          "acm:DeleteCertificate",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

