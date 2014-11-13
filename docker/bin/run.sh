#!/bin/bash
BRANCH=`git name-rev --name-only HEAD`
docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"
docker run -d --name=observations-uwsgi -p 8001 -e PREFIX=observations lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
docker run -d --name=observations-nginx -p 8000:8000 -e PREFIX=observations --link observations-uwsgi:observations-uwsgi lcogtwebmaster/lcogt:observations-nginx-$BRANCH
