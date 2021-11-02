#!/bin/bash
SESSION=$(AWS_PAGER="" aws sts assume-role --region us-east-1 --role-arn $ROLE_ARN --role-session-name terraform --region us-east-1 --output json)
unset AWS_PROFILE

unset AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=$(echo $SESSION | jq -r ".Credentials.AccessKeyId")

unset AWS_SECRET_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$(echo $SESSION | jq -r ".Credentials.SecretAccessKey")

unset AWS_SESSION_TOKEN
export AWS_SESSION_TOKEN=$(echo $SESSION | jq -r ".Credentials.SessionToken")

KEY=$( aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:077346344852:secret:db-ec2-key-pair-aofYm8  | jq --raw-output '.SecretString' )
DB_PASSWORD=$( aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:077346344852:secret:db-creds-WszNCl  | jq --raw-output '.SecretString' | jq -r .password )
DB_USERNAME=$( aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:077346344852:secret:db-creds-WszNCl  | jq --raw-output '.SecretString' | jq -r .username )
DB_HOST=$( aws rds describe-db-instances --region=us-east-1 --db-instance-identifier "test-mantarray-rds-one" | jq --raw-output ".[][].Endpoint.Address" )

ssh-agent -a /tmp/ssh_agent.sock > /dev/null
ssh-add - <<< "${KEY}"

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ./.github/schema/schema.sql ec2-user@ec2-54-226-191-183.compute-1.amazonaws.com:/tmp
ssh -o StrictHostKeyChecking=no ec2-user@ec2-54-226-191-183.compute-1.amazonaws.com "mysql -u $DB_USERNAME -p$DB_PASSWORD -h $DB_HOST < /tmp/schema.sql"
