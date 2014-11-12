NAME := lcogtwebmaster/lcogt
BRANCH := $(shell git name-rev --name-only HEAD)
BUILDDATE := $(shell date +%Y%m%d%H%M)
TAG1 := observations-uwsgi-${BRANCH}
TAG2 := observations-nginx-${BRANCH}

.PHONY: all uwsgi test login push

all: uwsgi nginx push

login:
    docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"

uwsgi:
	export BUILDDATE=${BUILDDATE} && export BRANCH=${BRANCH} && cat docker/uwsgi.dockerfile | envsubst > Dockerfile && docker build -t $(NAME):$(TAG1) --rm . && rm -f Dockerfile

nginx:
	export BUILDDATE=${BUILDDATE} && export BRANCH=${BRANCH} && cat docker/nginx.dockerfile | envsubst > Dockerfile && docker build -t $(NAME):$(TAG2) --rm . && rm -f Dockerfile

test:
	env NAME=${NAME} VERSION=${TAG1} ./test/runtests.sh

push: test login
	@if ! docker images ${NAME} | awk '{ print $$2 }' | grep -q -F ${TAG1}; then echo "${NAME}:${TAG1} is not yet built. Please run 'make'"; false; fi
	docker push ${NAME}:${TAG1} && docker push ${NAME}:${TAG2}
