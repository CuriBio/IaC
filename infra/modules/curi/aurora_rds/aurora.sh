#!/bin/bash
sudo yum update -y
sudo rpm -Uvh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
sudo yum install mysql-community-server
sudo systemctl enable mysqld
sudo systemctl start mysqld
mysql -u $1 -p$2 -h $3 -P $4 < /tmp/schema.sql;