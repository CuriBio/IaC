#!/bin/bash

# Connect to prod db and copy file to local directory
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region "us-east-1"

PROD_SESSION=$(AWS_PAGER="" aws sts assume-role --region us-east-1 --role-arn $PROD_ASSUMED_ROLE_ARN --role-session-name terraform --region us-east-1 --output json)
unset AWS_PROFILE

unset AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=$(echo $PROD_SESSION | jq -r ".Credentials.AccessKeyId")

unset AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$(echo $PROD_SESSION | jq -r ".Credentials.SecretAccessKey")

unset AWS_SESSION_TOKEN
export AWS_SESSION_TOKEN=$(echo $PROD_SESSION | jq -r ".Credentials.SessionToken")

PROD_KEY=$( aws secretsmanager get-secret-value --secret-id $PROD_DB_KEY_ARN | jq --raw-output '.SecretString' )
PROD_DB_PASSWORD=$( aws secretsmanager get-secret-value --secret-id $PROD_DB_CREDS_ARN  | jq --raw-output '.SecretString' | jq -r .password )
PROD_DB_USERNAME=$( aws secretsmanager get-secret-value --secret-id $PROD_DB_CREDS_ARN  | jq --raw-output '.SecretString' | jq -r .username )

eval $(ssh-agent -s)
ssh-agent -a /tmp/ssh_agent.sock > /dev/null
ssh-add - <<< "${PROD_KEY}"

ssh -o StrictHostKeyChecking=no $PROD_EC2_HOST "mysqldump -f -u $PROD_DB_USERNAME -p$PROD_DB_PASSWORD -h $PROD_DB_HOST --add-drop-database --set-gtid-purged=OFF --databases mantarray_recordings > /tmp/data_dump.sql"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r $PROD_EC2_HOST:/tmp/data_dump.sql /tmp

ssh-add -D
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

# Connect to specified db and dump prod data
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


ssh-add - <<< "${KEY}"

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/data_dump.sql $EC2_HOST:/tmp
ssh -o StrictHostKeyChecking=no $EC2_HOST "mysql -u $DB_USERNAME -p$DB_PASSWORD -h $DB_HOST < /tmp/data_dump.sql"

# clean up local dump file
rm /tmp/data_dump.sql
