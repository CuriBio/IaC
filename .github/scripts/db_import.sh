#!/bin/bash
chmod +x .github/scripts/configure_aws.sh
. .github/scripts/configure_aws.sh

eval $(ssh-agent -s)
ssh-agent -a /tmp/ssh_agent.sock > /dev/null
ssh-add - <<< "${KEY}"

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r $FILE_PATH $EC2_HOST:/tmp
ssh -o StrictHostKeyChecking=no $EC2_HOST "mysql -u $DB_USERNAME -p'$DB_PASSWORD' -h $DB_HOST < /tmp/$FILE_NAME"
