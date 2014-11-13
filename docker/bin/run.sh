#!/bin/bash
BRANCH=`git name-rev --name-only HEAD`
docker stop observations-uwsgi && docker rm observations-uwsgi > /dev/null
docker stop observations-nginx && docker rm observations-nginx > /dev/null
docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"
if [ "$DEBUG" != "" ]; then
    DEBUGENV="-e DEBUG=True"
fi
docker run -d --name=observations-uwsgi -p 8001 -e PREFIX=observations $DEBUGENV lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
docker run -d --name=observations-nginx -p 8000:8000 -e PREFIX=observations $DEBUGENV --link observations-uwsgi:observations-uwsgi lcogtwebmaster/lcogt:observations-nginx-$BRANCH
