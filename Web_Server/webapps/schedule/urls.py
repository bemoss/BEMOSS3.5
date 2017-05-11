from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^_submit_schedule/$', views.update_device_schedule, name='update-device-schedule'),
    url(r'^_activate_scheduler/$', views.activate_schedule),
    url(r'^([a-zA-Z0-9]+)/$', views.showSchedule, name='view-device-schedule')
]