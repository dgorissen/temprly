from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.template import RequestContext
from temprly.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django import forms
import sys
from django.core import serializers
from django.http import Http404
import gviz_api
import itertools
from django.contrib.auth.decorators import login_required
from temprly.utils import ratelimit
import settings
import md5
import hashlib

# TODO: overlap with edit_sensor
@login_required
def add_sensor(request, location_id):
    
    loc = Location.objects.filter(id=location_id)
    
    if not loc:
        raise Exception("No matching location found for id %s" % location_id)
    else:
        loc = loc[0]

    if request.method == 'GET':
        # return an empty form 
        form = SensorForm()
        form.fields['location'].empty_label = None
        form.fields['location'].initial = loc.id
        
        return HttpResponse(form.as_p())
    
    elif request.method == 'POST': 
        # If the form has been submitted...
        form = SensorForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            # save to DB
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=500)

@login_required
def del_sensor(request, location_id, sensor_id):

    # get the corresponding sensor
    sensor = Sensor.objects.filter(location__id=location_id, id=sensor_id)
    if not sensor:
        raise Exception("No matching sensor with id %s found at location %s" % (sensor_id,location_id))
    else:
        sensor.delete()
        return HttpResponse(status=200)

@login_required
def edit_sensor(request, location_id, sensor_id):
    
    # get the corresponding sensor
    sensor = Sensor.objects.filter(location__id=location_id, id=sensor_id)
    if not sensor:
        raise Exception("No matching sensor with id %s found at location %s" % (sensor_id,location_id))
    else:
        sensor = sensor[0]
        
    if request.method == 'GET':
        # return an empty form 
        form = SensorForm(instance=sensor)
        return HttpResponse(form.as_p())
    
    elif request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            # save to DB
            obj = form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
    else:
        return HttpResponse(status=500)

# TODO: support date ranges
@login_required
def get_readings(request, location_id, sensor_id):
    
    username = request.user.username
    format = request.GET.get("format","json")
    
    if request.method == "GET":
        loc = list(Location.objects.filter(id=location_id, owner=request.user))
        
        if not loc:
           raise Exception("No matching location found for id %s" % location_id)
        else:
            loc = loc[0]
        
        # first filter by location
        readings = SensorReading.objects.filter(sensor__location=loc)
        
        if sensor_id:
            # further filter by sensor if requested
            readings = readings.filter(sensor__id=sensor_id)
        
        if format == "gviz":
            # return data in the google visualization api format
            tqx = request.GET.get('tqx', None) 
            data = readings_to_gviz(readings, loc, tqx)
            return HttpResponse(data)
        elif format == "json":
            data = serializers.serialize(format, readings)
            return HttpResponse(data)
        else:
            raise Exception("Invalid data format %s requested" % format)
    else:
        return HttpResponse(status=500)

def readings_to_gviz(readings, loc, tqx):
    description = [("timestamp","datetime", "Time")]
    
    # each sensor is a column
    sensors = Sensor.objects.filter(location = loc).values('id','name') #.distinct()
    # keep track of which sensor goes into which column index
    name_map = {}
    for i,s in enumerate(sensors,start=1):
        description.append(("sensor_%s_val" % s['id'],"number", s['name']))
        name_map[s['name']] = i
        
    # the gviz api requires the same x value for each output value
    # however, not all sensors will fire at exactly the same time
    # by rounding to the nearest 5 minutes we force all sensors in lockstep
    # TODO: this computation happens every time you do a get...
    data = []
    for k,g in itertools.groupby(readings.order_by('timestamp'),
                                  key=lambda r : round_timestamp(r.timestamp)):
        
        item = [k]
        # not all sensors may have fired, so init with an empty row
        item.extend([None for _ in range(len(description)-1)])
        # for each sensor in the group of sensors that fired in this interval
        for r in g:
            idx = name_map[r.sensor.name]
            item[idx] = r.value
            
        data.append(item)
    
    # Load it into gviz_api.DataTable
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    # Creating a JSon string
    if tqx:
        params = dict([p.split(':') for p in tqx.split(';')]) 
        reqId = params['reqId'] 
        json = data_table.ToJSonResponse(req_id=reqId)
    else:
        json = data_table.ToJSon()
        
    return json

# Round a timestamp to the nearest nth minute
def round_timestamp(tm, round_to = 5):
    tm += timedelta(minutes=round_to / 2)
    tm -= timedelta(minutes=tm.minute % round_to)
    return tm

@login_required
def user_profile(request):
    data = {
            'token' : request.user.get_profile().token
            }
    return render_to_response('user_profile.html',data,context_instance=RequestContext(request))

@login_required
def usage(request):
    data = {
            'token' : request.user.get_profile().token
            }
    return render_to_response('usage.html',data,context_instance=RequestContext(request))

# limit the number of calls to this view
@ratelimit(limit=settings.REQ_PER_MIN,length=60)
@login_required
def add_reading(request, location_name = None, sensor_name = None, value = None):

    if not location_name:
        location_name = "Unassigned"
        
    if not sensor_name or not value:
        return HttpResponse(status=500)
    
    #TODO: change to POST
    if request.method == "POST":
        
        #get the token identifying the user
        token = request.POST.get('token',None)
        
        if not token:
            return HttpResponseForbidden()

        # is it a valid token
        up = UserProfile.objects.filter(token=token)
        if not up:
            return HttpResponseForbidden()
        else:
            up = up[0]
        
        # get the corresponding user
        user = up.user    
        
        # does the location already exist?
        loc = Location.objects.filter(name=location_name)
        if not loc:
            # if not, create it
            loc = Location(name=location_name,owner=user)
            loc.save()
        else:
            loc = loc[0]
        
        # does the sensor already exist?    
        sensor = Sensor.objects.filter(name=sensor_name, location=loc)
        if not sensor:
            # if not, create it
            sensor = Sensor(name=sensor_name, location=loc)
            sensor.save()
        else:
            sensor = sensor[0]
            
        #create the reading    
        reading = SensorReading(sensor=sensor, value=value)
        reading.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)

# remove a user and all his associated data
def delete_user(request):
    # remove all locations (will remove all sensors + readings as well)
    # djangos cascade should take care of the rest
    Location.objects.filter(owner=request.user).delete()
    request.user.delete()
    return HttpResponseRedirect('logout')

# register a new user
def register(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            pwd = request.POST['password1']
            user = authenticate(username=new_user.username, password=pwd)
            if user is not None:
                login(request, user)
            else:
                raise Exception("Problem authenticating user %s" % user.username)
    else:
        form = UserCreationForm()
 
    # return a new registration form   
    return render_to_response("register.html", {'form': form},context_instance=RequestContext(request))

@login_required
def get_locations(request):
    locations = Location.objects.filter(owner=request.user)
    return render_to_response('location_menu.html',{'locations':locations},context_instance=RequestContext(request))
    
@login_required
def del_location(request,location_id):
    Location.objects.filter(id=location_id).delete()
    return HttpResponse(status=200)

@login_required
def add_location(request):
    
    if request.method == 'GET': 
        # The client is asking for an empty form
        form = LocationForm()
        form.owner = request.user
        # get the html of the form
        return HttpResponse(form.as_p())
    
    elif request.method == 'POST': # If the form has been submitted...
        form = LocationForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['description']
            
            loc_obj = form.instance
            loc_obj.owner = request.user
            
            # save to DB
            loc_obj.save()
        else:
            # TODO:
            return HttpResponse(status=500)
    else:
        form = LocationForm() # An unbound form
        
    return render_to_response('main.html', {'location_form': form}, context_instance=RequestContext(request))

@login_required 
def home(request):
    locations = Location.objects.filter(owner=request.user)
    return render_to_response('main.html', {'locations':locations},context_instance=RequestContext(request))
