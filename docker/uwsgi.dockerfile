#
# observations app image (driven by uwsgi)
#
FROM lcogtwebmaster/lcogt:webbase
MAINTAINER LCOGT <webmaster@lcogt.net>
RUN yum -y update; yum clean all

ADD . /var/www/apps/observations
WORKDIR /var/www/apps/observations

RUN pip install -r pip-requirements.txt
RUN python manage.py syncdb --noinput --migrate;
RUN python manage.py collectstatic --noinput;

ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings
ENV BRANCH ${BRANCH}
ENV BUILDDATE ${BUILDDATE}
ENV PREFIX ${PREFIX}

EXPOSE 8001

CMD ["/var/www/apps/observations/docker/bin/uwsgi.sh"]
