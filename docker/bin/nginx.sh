#!/bin/bash
touch /var/log/nginx/error.log
touch /var/log/nginx/access.log
mkdir -p /run
tail --pid $$ -f /var/log/nginx/access.log &
tail --pid $$ -f /var/log/nginx/error.log &
cat /var/www/apps/observations/docker/config/nginx.conf | envsubst > /etc/nginx/nginx.conf
/usr/sbin/nginx -c /etc/nginx/nginx.conf
