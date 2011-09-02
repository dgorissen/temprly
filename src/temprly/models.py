from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from temprly.utils import gen_token

class Location(models.Model):
    name = models.CharField(max_length=30, default="Unassigned")
    description = models.TextField(blank=True)
    # no need to add a member to the users table
    owner = models.ForeignKey(User, related_name='+')

    def __unicode__(self):
        return self.name

class Sensor(models.Model):
    # Simple list of sensor types
    # TODO: proper objects for units and types
    # TODO: would like sensor name + location as composite primary key, not supported by django yet
    SENSOR_TYPES = ( (u'T', u'Temperature'),
                     (u'H', u'Humidity'),
                     (u'?', u'Unknown')
                   )
    name = models.CharField(max_length=30, blank=False)
    type = models.CharField(max_length=30, blank=False, choices=SENSOR_TYPES, default=SENSOR_TYPES[0][1])
    description = models.TextField(blank=True)    
    location = models.ForeignKey(Location,related_name="sensor_list", blank=False)

    def __unicode__(self):
        return self.name

# the value of a sensor at a specific point in time
class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, related_name="reading_list")
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

# user profile, mainly just to hold his personal token
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=40, blank=False)

# Create the profile & token when the user is saved
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        token = gen_token(instance)
        UserProfile.objects.create(user=instance, token=token)
        
post_save.connect(create_user_profile, sender=User)

# Model forms, automatically generated
# TODO: customize L&F
class SensorReadingForm(ModelForm):
    class Meta:
        model = SensorReading
        
class SensorForm(ModelForm):
    class Meta:
        model = Sensor

class LocationForm(ModelForm):
    class Meta:
        model = Location
        exclude = ('owner',)
            