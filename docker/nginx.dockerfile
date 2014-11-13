#
# observations nginx container
#
FROM centos:centos6
MAINTAINER LCOGT <webmaster@lcogt.net>
RUN yum -y update; yum clean all
RUN yum -y install epel-release; yum clean all
RUN yum -y install nginx; yum clean all
RUN yum -y install python-pip; yum clean all
RUN yum -y install mysql-devel; yum clean all
RUN yum -y groupinstall "Development Tools"; yum clean all
RUN yum -y install python-devel; yum clean all

ADD . /var/www/apps/observations
WORKDIR /var/www/apps/observations
RUN cat docker/config/nginx.conf | envsubst > /etc/nginx/nginx.conf

RUN pip install pip==1.3
RUN pip install -r pip-requirements.txt
RUN python manage.py collectstatic --noinput;

ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings
ENV BRANCH ${BRANCH}
ENV BUILDDATE ${BUILDDATE}
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV PREFIX ${PREFIX}

EXPOSE 8000

CMD ["/var/www/apps/observations/docker/bin/nginx.sh"]

