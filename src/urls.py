from django.conf.urls.defaults import *
from django.contrib.auth.forms import AuthenticationForm

urlpatterns = patterns('',
    (r'^temprly/', include('temprly.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/temprly/', }),
)
