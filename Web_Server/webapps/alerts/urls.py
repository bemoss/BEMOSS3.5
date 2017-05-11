from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^alerts', views.alerts, name='alerts-alarm-settings'),
    url(r'^ntfns', views.notifications, name='alerts-notifications'),
    url(r'^create_alert', views.create_alert, name='create-alert'),
    url(r'^delete_alert', views.delete_alert, name='delete-alert'),
]