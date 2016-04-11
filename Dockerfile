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
EXPOSE 80
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings

# Default prefix
ENV PREFIX /observations

# Install packages and update base system
RUN yum -y install epel-release \
        && yum -y install cronie libjpeg-devel nginx python-pip mysql-devel python-devel supervisor \
        && yum -y groupinstall "Development Tools" \
        && yum -y install ImageMagick \
        && yum -y install 'http://www.astromatic.net/download/stiff/stiff-2.4.0-1.x86_64.rpm' \
        && yum -y install 'http://www.astromatic.net/download/sextractor/sextractor-2.19.5-1.x86_64.rpm' \
        && yum -y update \
        && yum -y clean all

# Install the Python required packages
COPY app/requirements.pip /var/www/apps/observations/requirements.pip
RUN pip install uwsgi==2.0.8 \
    && pip install -r /var/www/apps/observations/requirements.pip \
    && pip install astroscrappy

# Copy configuration files
COPY config/init /init
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# Copy the LCOGT Mezzanine webapp files
COPY app /var/www/apps/observations
