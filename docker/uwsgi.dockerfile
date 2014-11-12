#
# observations app container
#
FROM centos:centos6
MAINTAINER LCOGT <webmaster@lcogt.net>
RUN yum -y update; yum clean all
RUN yum -y install epel-release; yum clean all
RUN yum -y install python-pip; yum clean all
RUN yum -y install mysql-devel; yum clean all
RUN yum -y groupinstall "Development Tools"; yum clean all
RUN yum -y install python-devel; yum clean all

ADD . /var/www/apps/observations
WORKDIR /var/www/apps/observations

RUN pip install pip==1.3;  pip install uwsgi==2.0.8
RUN pip install -r pip-requirements.txt
RUN python manage.py syncdb --noinput --migrate;
RUN python manage.py collectstatic --noinput;
RUN python manage.py loaddata observations/fixtures/site.json
RUN python manage.py loaddata observations/fixtures/filter.json
RUN python manage.py loaddata observations/fixtures/telescope.json
RUN python manage.py loaddata observations/fixtures/image.json
RUN python manage.py loaddata observations/fixtures/observationstats.json

ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings
ENV BRANCH ${BRANCH}
ENV BUILDDATE ${BUILDDATE}

EXPOSE 8000
CMD ["/usr/bin/uwsgi", "--ini", "/var/www/apps/observations/config/uwsgi.ini"]
