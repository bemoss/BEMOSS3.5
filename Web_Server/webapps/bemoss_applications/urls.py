from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.application_main, name='application-main'),
    url(r'^app_add/$', views.application_add),
    url(r'^command/save_start/$', views.save_and_start, name='save_and_start'),
    url(r'^command/calibrate/$', views.calibrate, name='iblc-app-calibrate'),
    url(r'^command/update_target/$', views.update_target_illuminance, name='update-illuminance'),
    url(r'^command/delete/([_a-zA-Z0-9]+)$', views.application_remove, name='delete-appliation'),
    url(r'([_a-zA-Z0-9]+)/$', views.application_individual, name='application-individual'),

]