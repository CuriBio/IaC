#!/bin/bash
chmod +x .github/scripts/configure_aws.sh
. .github/scripts/configure_aws.sh

eval $(ssh-agent -s)
ssh-agent -a /tmp/ssh_agent.sock > /dev/null
ssh-add - <<< "${KEY}"

ssh -o StrictHostKeyChecking=no $EC2_HOST "mysqldump -f -u $DB_USERNAME -p$DB_PASSWORD -h $DB_HOST --add-drop-database --set-gtid-purged=OFF --databases mantarray_recordings > /tmp/data_dump.sql"
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r $EC2_HOST:/tmp/data_dump.sql /tmp

eval $(ssh-agent -k)
rm -rf /tmp/ssh_agent.sock
