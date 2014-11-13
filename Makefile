#-----------------------------------------------------------------------------------------------------------------------
# observations docker image makefile
#
# 'make' will create the two docker images needed to run the observations app:
#    lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
#    lcogtwebmaster/lcogt:observations-nginx-$BRANCH
#
# where $BRANCH is the git branch name presently in use.
#
# Once built, these images can be pushed up the docker hub repository via 'make install',
# and can then be run via something like:
#
# docker run -d --name=observations-wsgi -p 8001 -e PREFIX=observations2 lcogtwebmaster/lcogt:observations-uwsgi-$BRANCH
# docker run -d --name=observations-nginx -p 8000:8000 -e PREFIX=observations2 --link observations-wsgi:observations-wsgi lcogtwebmaster/lcogt:observations-nginx-$BRANCH
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
TAG1 := observations-uwsgi-${BRANCH}
TAG2 := observations-nginx-${BRANCH}
PREFIX := observations

.PHONY: all uwsgi nginx test login push_wsgi push_nginx install

all: uwsgi nginx test

login:
    docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"

uwsgi:
	export BUILDDATE=${BUILDDATE} && \
	export BRANCH=${BRANCH} && \
	export PREFIX=${PREFIX} && \
	cat docker/uwsgi.dockerfile | envsubst > Dockerfile && \
	docker build -t $(NAME):$(TAG1) --rm . && rm -f Dockerfile

nginx:
	export BUILDDATE=${BUILDDATE} && \
	export BRANCH=${BRANCH} && \
	export PREFIX=${PREFIX} && \
	cat docker/nginx.dockerfile | envsubst > Dockerfile && \
	docker build -t $(NAME):$(TAG2) --rm . && rm -f Dockerfile

test:
	env NAME=${NAME} VERSION=${TAG1} ./test/runtests.sh

push_wsgi: login
	@if ! docker images ${NAME} | awk '{ print $$2 }' | grep -q -F ${TAG1}; then echo "${NAME}:${TAG1} is not yet built. Please run 'make'"; false; fi
    docker push ${NAME}:${TAG1}

push_nginx: login
	@if ! docker images ${NAME} | awk '{ print $$2 }' | grep -q -F ${TAG2}; then echo "${NAME}:${TAG2} is not yet built. Please run 'make'"; false; fi
    docker push ${NAME}:${TAG2}

install: push_wsgi push_nginx
