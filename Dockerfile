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
# docker build -t registry.lcogt.net/observations:latest .
#
# Push to Registry with
# docker push registry.lcogt.net/observations:latest
#
# To run with nginx + uwsgi both exposed:
# docker run -d -p 8000:80 -p 9090:8001 -m="128m" --name=observations registry.lcogt.net/observations:latest
#
################################################################################
FROM centos:centos7
MAINTAINER LCOGT <webmaster@lcogt.net>

# Install packages and update base system
RUN yum -y install epel-release \
        && yum -y install nginx supervisor \
        && yum -y install gcc make mysql-devel python-devel python-pip \
        && yum -y update \
        && yum -y clean all

# nginx runs on port 80, uwsgi runs on port 9090
EXPOSE 80 9090

# The entry point is our init script, which runs startup tasks, then
# execs the supervisord daemon
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE observations.settings

# Copy configuration files
COPY config/init /init
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# Copy the LCOGT Mezzanine webapp files
COPY app /var/www/apps/observations

# Install the Python required packages
RUN pip install pip==1.3 && pip install uwsgi==2.0.8 \
        && pip install -r /var/www/apps/observations/pip-requirements.txt

# Setup the LCOGT Observations webapp
RUN python /var/www/apps/observations/manage.py collectstatic --noinput
# If any schema changed have happened but not been applied
RUN python /var/www/apps/observations/manage.py syncdb --noinput
RUN python /var/www/apps/observations/manage.py migrate --noinput
