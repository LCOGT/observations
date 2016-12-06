FROM centos:7
MAINTAINER LCOGT <webmaster@lcogt.net>

EXPOSE 80
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings

# Default prefix
ENV PREFIX /observations

# Install packages and update base system
RUN yum -y install epel-release \
        && yum -y install MySQL-python nginx python-pip supervisor uwsgi-plugin-python \
        && yum -y update \
        && yum -y clean all

# Install the Python required packages
COPY app/requirements.pip /var/www/apps/observations/requirements.pip
RUN pip install -r /var/www/apps/observations/requirements.pip \
        && rm -rf ~/.cache/pip

# Copy configuration files
COPY config/init /init
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# Copy the LCOGT Mezzanine webapp files
COPY app /var/www/apps/observations
