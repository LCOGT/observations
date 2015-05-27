observations
============

This is the part of the [LCOGT](http://lcogt.net/) site that aims to ensure
every observation taken by a public user of the network has a permanent web
presence. The aim is to provide access through
[RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer) URLs.
Observations can be viewed in a variety of ways:

* [/observations/coj/2m0a/55996](http://lcogt.net/observations/coj/2m0a/55996) - a specific observation
* [/observations/coj/2m0a](http://lcogt.net/observations/coj/2m0a) - all results for a specific telescope at a site (0m4a, 1m0a, 2m0a)
* [/observations/coj](http://lcogt.net/observations/coj) - all results for a specific site using the 3 letter site codes
* [/observations/recent](http://lcogt.net/observations/recent) - the most recent observations
* [/observations/popular](http://lcogt.net/observations/popular) - the all-time most popular observations
* [/observations/trending](http://lcogt.net/observations/trending) - a combination of popularity and recency
* [/observations/user/4658](http://lcogt.net/observations/user/4658) - all results for a specific user (RTI ID numbers)
* [/observations/category](http://lcogt.net/observations/category) - a list of [AVM](http://www.virtualastronomy.org/avm_metadata.php) categories
* [/observations/category/galaxies](http://lcogt.net/observations/category/galaxies) - all results for major [AVM](http://www.virtualastronomy.org/avm_metadata.php) categories
* [/observations/category/5.5.2](http://lcogt.net/observations/category/5.5.2) - all results for a specific [AVM](http://www.virtualastronomy.org/avm_metadata.php) category
* [/observations/map](http://lcogt.net/observations/map) - a heat map of observations within the past month
* [/observations/object/M42](http://lcogt.net/observations/object/M42) - named astronomical objects have a breakdown of their exposure times

Groups of observations can be viewed in a variety of formats:

* HTML - the default
* HTML-based slideshow - add `/show` to the URL
* [JSON](https://en.wikipedia.org/wiki/JSON) and [JSON-p](https://en.wikipedia.org/wiki/JSONP): add `.json` or `.json?callback=blah` to the URL
* [KML](https://en.wikipedia.org/wiki/Keyhole_Markup_Language): add `.kml` to the URL
* [RSS](https://en.wikipedia.org/wiki/RSS): add `.rss` to the URL

Docker stuff
============

A production deployment of this application requires only a single container,
which contains both uwsgi (for the Python Django application) and nginx (to
serve the static content).

The following environment variables are available to customize the behavior
of the container:

* PREFIX - determines the root URI for the application (default: "")
* DEBUG - enables debugging within the Django application (default: False)

To build and run the Docker image for this application, just run:

    $ docker build -t observations_test .
    $ docker run -p 8888:80 --name obs -e PREFIX=/observations -m 256m observations_test

To build a production Docker image:

    $ docker build -t registry.lcogt.net/observations:release
    $ docker push registry.lcogt.net/observations:release
