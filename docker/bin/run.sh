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
docker run -d --name=observations_uwsgi -e PREFIX=/observations $DEBUGENV lcogtwebmaster/lcogt:observations_uwsgi_$BRANCH
docker run -d --name=observations_nginx -p 8000:8000 -e PREFIX=/observations $DEBUGENV --link observations_uwsgi:observations_uwsgi lcogtwebmaster/lcogt:observations_nginx_$BRANCH
if [ "$DEBUG" != "" ]; then
    docker logs -f observations_nginx &
    docker logs -f observations_uwsgi &
fi