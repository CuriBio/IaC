#!/bin/bash
set -ex

aws --version
SESSION=$(AWS_PAGER="" aws sts assume-role --region us-east-1 --role-arn $ROLE_ARN --role-session-name terraform --region us-east-1 --output json --debug)
echo $SESSION
unset AWS_PROFILE

unset AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=$(echo $SESSION | jq -r ".Credentials.AccessKeyId")

unset AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$(echo $SESSION | jq -r ".Credentials.SecretAccessKey")

unset AWS_SESSION_TOKEN
export AWS_SESSION_TOKEN=$(echo $SESSION | jq -r ".Credentials.SessionToken")

aws ecr get-login-password --region us-east-1 | docker login --password-stdin --username AWS $ECR_REPO
docker push $ECR_REPO:"$TAG"
