rtiobservations
===============

The LCOGT Real Time Interface (RTI) Django project. 


[/observations](http://lcogt.net/observations)
=============

This is the part of the [LCOGT](http://lcogt.net/) site that aims to ensure every observation taken by a public user of the network has a permanent web presence. The aim is to provide access through [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer) URLs. Observations can be viewed in a variety of ways:

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

The output format of groups of observations can be returned in a variety of formats:

* HTML - the default
* [JSON](https://en.wikipedia.org/wiki/JSON) and [JSON-p](https://en.wikipedia.org/wiki/JSONP): add `.json` or `.json?callback=blah` to the URL
* [KML](https://en.wikipedia.org/wiki/Keyhole_Markup_Language): add `.kml` to the URL
* [RSS](https://en.wikipedia.org/wiki/RSS): add `.rss` to the URL
