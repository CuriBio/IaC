#!/bin/bash
set -ex

aws --version
aws sts assume-role --role-arn $ROLE_ARN --role-session-name terraform
unset AWS_PROFILE

unset AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=$(echo $SESSION | jq -r ".Credentials.AccessKeyId")

unset AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$(echo $SESSION | jq -r ".Credentials.SecretAccessKey")

unset AWS_SESSION_TOKEN
export AWS_SESSION_TOKEN=$(echo $SESSION | jq -r ".Credentials.SessionToken")

aws ecr get-login-password --region us-east-1 | docker login --password-stdin --username AWS $ECR_REPO
docker push $ECR_REPO:"$TAG"
