#!/bin/bash
ASSUMED_ROLE_ARN=$1
DB_KEY_ARN=$2
DB_CREDS_ARN=$3
DB_HOST=$4
EC2_HOST=$5

aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region "us-east-1"

SESSION=$(AWS_PAGER="" aws sts assume-role --region us-east-1 --role-arn $ASSUMED_ROLE_ARN --role-session-name terraform --region us-east-1 --output json)
unset AWS_PROFILE

unset AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=$(echo $SESSION | jq -r ".Credentials.AccessKeyId")

unset AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$(echo $SESSION | jq -r ".Credentials.SecretAccessKey")

unset AWS_SESSION_TOKEN
export AWS_SESSION_TOKEN=$(echo $SESSION | jq -r ".Credentials.SessionToken")

KEY=$( aws secretsmanager get-secret-value --secret-id $DB_KEY_ARN | jq --raw-output '.SecretString' )
DB_PASSWORD=$( aws secretsmanager get-secret-value --secret-id $DB_CREDS_ARN  | jq --raw-output '.SecretString' | jq -r .password )
DB_USERNAME=$( aws secretsmanager get-secret-value --secret-id $DB_CREDS_ARN  | jq --raw-output '.SecretString' | jq -r .username )

alembic upgrade head

HISTORY=$( alembic history --verbose )
echo $HISTORY
