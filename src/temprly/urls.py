# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', r'temprly.views.home'),
    (r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^register$', r'temprly.views.register'),
    (r'^profile$', r'temprly.views.user_profile'),
    (r'^deluser$', r'temprly.views.delete_user'),
    (r'^usage$', r'temprly.views.usage'),
    # POST readings/add/<location>/<sensor>/value
    # POST readings/add/<sensor>/value (location = unassigned assumed)
    (r'^readings/add/(?:(?P<location_name>\w+)/)?(?P<sensor_name>\w+)/(?P<value>\d+)$', r'temprly.views.add_reading'),

    # TODO: support for getting date ranges
    # GET readings/<location>/<sensor>
    # GET readings/<location>
    (r'^readings/(?P<location_id>\d+)(?:/(?P<sensor_id>\d+))?$', r'temprly.views.get_readings'),
    
    (r'^sensors/edit/(?P<location_id>\d+)/(?P<sensor_id>\d+)$', r'temprly.views.edit_sensor'),
    (r'^sensors/add/(?P<location_id>\d+)$', r'temprly.views.add_sensor'),
    (r'^sensors/del/(?P<location_id>\d+)/(?P<sensor_id>\d+)$', r'temprly.views.del_sensor'),

    (r'^locations/del/(?P<location_id>\d+)$', r'temprly.views.del_location'),
    (r'^add_location$',r'temprly.views.add_location'),
    (r'^get_locations$',r'temprly.views.get_locations'),
)
