
from django import template
from django.utils.timesince import timesince
from datetime import datetime
from django.core.serializers import serialize
from django.db.models.query import QuerySet
import simplejson
from django.utils.safestring import mark_safe
from django.template import Library
from bemoss_lib.utils import date_converter
register = template.Library()
import pytz

#Time to minutes converter for Notifications bar
#TODO test
@register.filter
def timedelta(value, arg=None):
    if not value:
        return ''
    if value.tzinfo != pytz.UTC:
        value = date_converter.localToUTC(value)
    else:
        value=value.replace(tzinfo=None) #no tzone is assumed UTC
    if arg:
        cmp = arg
    else:
        cmp = datetime.utcnow()
    if value > cmp:
        return "in %s" % timesince(cmp, value)
    else:
        return "%s ago" % timesince(value, cmp)

@register.filter
def as_local_time(user_datetime):
    if user_datetime:
        return date_converter.toLocal(user_datetime).replace(tzinfo=None)
    else:
        return user_datetime

#register.filter('timedelta',timedelta)
def device_data_jsonify(device_data):

    if isinstance(device_data, QuerySet):
        device_data = serialize('json', device_data)

    data_dict = device_data.data
    data_dict['agent_id'] = device_data.agent_id
    if 'device_model_id' in data_dict:
        data_dict.pop('device_model_id')


    return mark_safe(simplejson.dumps(data_dict))

register.filter('device_data_jsonify', device_data_jsonify)
device_data_jsonify.is_safe = True