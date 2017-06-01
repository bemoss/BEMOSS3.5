# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.simple_tag
def strtimerange(starthour,minute_interval,endhour):
    ret_list = []
    minute = (starthour - int(starthour))*60
    starthour = int(starthour)
    while starthour < endhour:
        ret_list.append({'str':str(starthour)+":"+"%02d" % (minute,),'val':starthour+minute/60})
        minute += minute_interval
        if minute >= 60:
            starthour += 1
            minute -= 60
    return ret_list

@register.simple_tag
def strhourrange(starthour,endhour):
    ret_list = []
    for hr in range(starthour,endhour+1):
        ret_list.append({'str':str(hr)+" hr" , 'val':hr})
    return ret_list


@register.simple_tag
def strtemprange(starttemp,step,endtemp):
    ret_list = []
    while starttemp <= endtemp:
        ret_list.append({'str':str(starttemp) + u'°F','val':starttemp})
        starttemp += step
    return  ret_list

