Motivation
==========

The proverbial itch for Temprly was simple:

* deploy a bunch of temperature/humidity/.. sensors around the house
* have them send their readings to a remote website
* visualize, browse, analyze the data online

I did not immediately find something suitable and I was keen to learn something new (the main motivation).
So I bought an Arduino with Ethernet shield and started reading some tutorials on Django, JQuery, and Google App Engine.
Three things I wanted to get more familiar with.

Status
=======

**The good:**

All the basic functionality is there: registering, adding locations, sensors, submitting readings RESTfully & simple visualization
using the Google Visualization API.  All hosted on App Engine at www.temprly.com

**The bad:**

The current code is the very basic, bare bones functionality.  There are still many TODOs, features, improvements left to do.
Some of the things I originally had in mind:

* multiple sensor types & units
* sensor correlation & comparisons
* aggregate statistics
* predictions
* proper sensor authentication
* OpenID/OAuth
* link to the outside weather
* smartphone/tablet App
* ... 

Unfortunately, I will not be able to work on it much more in the future.  The reason simply being that life has caught up with
my spare time: moving countries, buying & DIY'ing a house, becoming a dad, full time job, etc. 

I will continue to tweak things here or there, but at least there is a record that something was done and something was learned.

**The Ugly:**

My graphical design abilities rival those of a drunken lemur and being colorblind does not exactly help :)  I have used JQueryUI for
the basic theming but it really needs somebody with a talent for design & CSS to revamp.  Its just not my thing.


Running the code
==================

To run and use the code:

* Download and install the `GAE Python SDK <http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python>`_. 
* Follow the `Django-nonrel installation instructions <http://www.allbuttonspressed.com/projects/djangoappengine>`_.  
* Make sure autoload, dbindexer, django, djangoappengine, djangotoolbox are linked into the src folder.
* running "python manage.py" should get you going.

Thoughts, comments, questions? Drop me a line at dgorissen@gmail.com
