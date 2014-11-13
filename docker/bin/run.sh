#!/bin/bash
export BRANCH= $(git name-rev --name-only HEAD)
docker run -d --name=observations-wsgi -p 8001 -e PREFIX=observations lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
docker run -d --name=observations-nginx -p 8000:8000 -e PREFIX=observations --link observations-wsgi:observations-wsgi lcogtwebmaster/lcogt:observations-nginx-$BRANCH
