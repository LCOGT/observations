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
COPY config/nginx.conf /etc/nginx/

RUN pip install pip==1.3
RUN pip install -r pip-requirements.txt
RUN python manage.py collectstatic --noinput;

ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings
ENV BRANCH ${BRANCH}
ENV BUILDDATE ${BUILDDATE}

EXPOSE 8001

CMD ["/usr/sbin/nginx", "-c", "/etc/nginx/nginx.conf"]

