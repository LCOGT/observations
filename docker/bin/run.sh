#!/bin/bash
BRANCH=`git name-rev --name-only HEAD`
docker stop observations-uwsgi 2>&1 > /dev/null
docker rm observations-uwsgi 2>&1 > /dev/null
docker stop observations-nginx 2>&1 > /dev/null
docker rm observations-nginx 2>&1 > /dev/null
docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"
if [ "$DEBUG" != "" ]; then
    DEBUGENV="-e DEBUG=True"
fi
docker run -d --name=observations-uwsgi -p 8001 -e PREFIX=/observations $DEBUGENV lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
docker run -d --name=observations-nginx -p 8000:8000 -e PREFIX=/observations $DEBUGENV --link observations-uwsgi:observations-uwsgi lcogtwebmaster/lcogt:observations-nginx-$BRANCH
if [ "$DEBUG" != "" ]; then
    docker logs -f observations-nginx &
    docker logs -f observations-uwsgi &
fi