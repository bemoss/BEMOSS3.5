from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^_update/$', views.submit_devicedata),
    url(r'([a-zA-Z0-9]+)/$', views.devicedata_view, name='device-view-device')
]