#-----------------------------------------------------------------------------------------------------------------------
# observations docker image makefile
#
# 'make' will create the docker image needed to run the observations app:
#    lcogtwebmaster/lcogt:observations_$BRANCH
#
# where $BRANCH is the git branch name presently in use.
#
# Once built, this image can be pushed up the docker hub repository via 'make install',
# and can then be run via something like:
#
# docker run -d --name=observations_wsgi -e PREFIX=/observations2 lcogtwebmaster/lcogt:observations_$BRANCH /var/www/apps/observations/docker/bin/uwsgi.sh
# docker run -d --name=observations_nginx -p 8000:8000 -e PREFIX=/observations2 --link observations_wsgi:observations_wsgi lcogtwebmaster/lcogt:observations_$BRANCH /var/www/apps/observations/docker/bin/nginx.sh
#
# at which point the app will be exposed on the target host at port 8000
#
# Doug Thomas
# LCOGT
#
#-----------------------------------------------------------------------------------------------------------------------
NAME := lcogtwebmaster/lcogt
BRANCH := $(shell git name-rev --name-only HEAD)
BUILDDATE := $(shell date +%Y%m%d%H%M)
TAG0 := webbase
TAG1 := observations_${BRANCH}
PREFIX := '/observations'

.PHONY: all observations test login install

all: webbase observations test

login:
	docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"

webbase:
	cat docker/webbase.dockerfile | envsubst > Dockerfile && \
	docker build -t $(NAME):$(TAG0) --rm . && rm -f Dockerfile

observations:
	export BUILDDATE=${BUILDDATE} && \
	export BRANCH=${BRANCH} && \
	export PREFIX=${PREFIX} && \
	cat docker/observations.dockerfile | envsubst > Dockerfile && \
	docker build -t $(NAME):$(TAG1) --rm . && rm -f Dockerfile

test:
	env NAME=${NAME} VERSION=${TAG1} ./test/runtests.sh

install: test login
	@if ! docker images ${NAME} | awk '{ print $$2 }' | grep -q -F ${TAG1}; then echo "${NAME}:${TAG1} is not yet built. Please run 'make'"; false; fi
	docker push ${NAME}:${TAG1}
