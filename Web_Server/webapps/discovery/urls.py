from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^mdiscover', views.discover_devices, name='discovery-manual-discover'),
    url(r'^new', views.discover_new_devices),
    url(r'^authenticate_device', views.authenticate_device, name='discovery-authenticate-device')
]