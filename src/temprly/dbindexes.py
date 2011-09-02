from temprly.models import *
from dbindexer.lookups import StandardLookup
from dbindexer.api import register_index

register_index(SensorReading, {'sensor__name': StandardLookup(),
                               'sensor__location': StandardLookup(),
                               'sensor__location__name': StandardLookup(),
                               'sensor__location__id': StandardLookup(),
                               'sensor__location__owner__username': StandardLookup(),
})
