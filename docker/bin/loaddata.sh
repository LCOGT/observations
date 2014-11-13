#!/bin/bash
cd /var/www/apps/observations
python manage.py loaddata observations/fixtures/site.json
python manage.py loaddata observations/fixtures/filter.json
python manage.py loaddata observations/fixtures/telescope.json
python manage.py loaddata observations/fixtures/image.json
python manage.py loaddata observations/fixtures/observationstats.json

