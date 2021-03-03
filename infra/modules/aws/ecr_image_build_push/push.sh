#!/bin/bash
set -ex

eval $(/usr/local/bin/aws sts assume-role --role-arn $ROLE_ARN --role-session-name terraform | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)\n"')
unset AWS_PROFILE
env
/usr/local/bin/aws ecr get-login-password --region us-east-1 | docker login --password-stdin --username AWS $ECR_REPO

docker push $ECR_REPO:"$TAG"
