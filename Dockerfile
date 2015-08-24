################################################################################
#
# Runs the LCOGT Python Django Observations webapp using nginx + uwsgi
#
# The decision to run both nginx and uwsgi in the same container was made because
# it avoids duplicating all of the Python code and static files in two containers.
# It is convenient to have the whole webapp logically grouped into the same container.
#
# You can choose to expose the nginx and uwsgi ports separately, or you can
# just default to using the nginx port only (recommended). There is no
# requirement to map all exposed container ports onto host ports.
#
# Build with
# docker build -t docker.lcogt.net/observations:latest .
#
# Push to Docker registry with
# docker push docker.lcogt.net/observations:latest
#
################################################################################

FROM centos:centos7
MAINTAINER LCOGT <webmaster@lcogt.net>

# The entry point is our init script, which runs startup tasks, then
# execs the supervisord daemon
ENTRYPOINT [ "/init" ]

# nginx runs on port 80, uwsgi runs on port 9090
EXPOSE 80

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings

# Default prefix
ENV PREFIX /observations

# Install packages and update base system
RUN yum -y install epel-release \
        && yum -y install nginx supervisor \
        && yum -y install gcc make mysql-devel python-devel python-pip \
        && yum -y update \
        && yum -y clean all

# Install the Python required packages
COPY app/requirements.txt /var/www/apps/observations/requirements.txt
RUN pip install pip==1.3 && pip install uwsgi==2.0.8 \
        && pip install -r /var/www/apps/observations/requirements.txt

# Copy configuration files
COPY config/init /init
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# Copy the LCOGT Mezzanine webapp files
COPY app /var/www/apps/observations
