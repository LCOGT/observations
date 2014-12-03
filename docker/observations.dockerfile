#
# observations dockerfile
#
FROM lcogtwebmaster/lcogt:webbase
MAINTAINER LCOGT <webmaster@lcogt.net>
RUN yum -y update; yum clean all

ADD . /var/www/apps/observations
WORKDIR /var/www/apps/observations
RUN cat docker/config/nginx.conf | envsubst '$PREFIX $OBSERVATIONS_UWSGI_PORT_8001_TCP_ADDR' > /etc/nginx/nginx.conf

RUN pip install -r pip-requirements.txt
RUN python manage.py collectstatic --noinput;

ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings
ENV BRANCH ${BRANCH}
ENV BUILDDATE ${BUILDDATE}
ENV PREFIX ${PREFIX}

EXPOSE 8000
EXPOSE 8001
