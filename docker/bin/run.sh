#!/bin/bash
BRANCH=`git name-rev --name-only HEAD`
docker stop observations_uwsgi 2>&1 > /dev/null
docker rm observations_uwsgi 2>&1 > /dev/null
docker stop observations_nginx 2>&1 > /dev/null
docker rm observations_nginx 2>&1 > /dev/null
docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"
if [ "$DEBUG" != "" ]; then
    DEBUGENV="-e DEBUG=True"
fi
if [ "$PREFIX" == "" ]; then
    PREFIX="/observations"
fi
docker run -d --name=observations_uwsgi -e PREFIX=$PREFIX $DEBUGENV lcogtwebmaster/lcogt:observations_$BRANCH /var/www/apps/observations/docker/bin/uwsgi.sh
docker run -d --name=observations_nginx -p 8000:8000 -e PREFIX=$PREFIX $DEBUGENV --link observations_uwsgi:observations_uwsgi lcogtwebmaster/lcogt:observations_$BRANCH /var/www/apps/observations/docker/bin/nginx.sh
if [ "$DEBUG" != "" ]; then
    docker logs -f observations_nginx &
    docker logs -f observations_uwsgi &
fi