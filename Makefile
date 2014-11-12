NAME := lcogtwebmaster/lcogt
BRANCH := $(shell git name-rev --name-only HEAD)
TAG := observations-${BRANCH}

.PHONY: all uwsgi test login push

all: uwsgi

login:
    docker login --username="lcogtwebmaster" --password="lc0GT!" --email="webmaster@lcogt.net"

uwsgi:
	export BRANCH=${BRANCH} && cat uwsgi.dockerfile | envsubst > Dockerfile && docker build -t $(NAME):$(TAG) --rm . && rm -f Dockerfile

test:
	env NAME=$(NAME) VERSION=$(TAG) ./test/runtests.sh

push: test login
	@if ! docker images $(NAME) | awk '{ print $$2 }' | grep -q -F $(TAG); then echo "$(NAME):$(TAG) is not yet built. Please run 'make build'"; false; fi
	docker push $(NAME):$(TAG)
