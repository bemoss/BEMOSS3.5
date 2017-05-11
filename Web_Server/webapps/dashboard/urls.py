from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.bemoss_home, name='index'),
    url(r'^discover$', views.discover, name='dashboard-discover-devices'),
    url(r'^change_zones$', views.change_zones, name='dashboard-change-zones'),
    url(r'^nwstat$', views.node_status, name='dashboard-node-status'),
    url(r'^dstat$', views.device_status, name='dashboard-device-status'),
    url(r'^export$', views.export_all_device_information),
    url(r'^bemoss_settings', views.bemoss_settings, name='dashboard-bemoss-settings'),
    url(r'^update_zip', views.update_zip, name='dashboard-zipcode-update'),
    url(r'^delete_holiday', views.delete_holiday, name='dashboard-holiday-delete'),
    url(r'^add_holiday', views.add_holiday, name='dashboard-holiday-add'),
    url(r'^save_zone_nickname_change$', views.save_zone_nickname_change, name='save_view_edit_changes_dashboard'),
    url(r'^save_node_nickname_change$', views.save_node_nickname_change, name='save-node-nickname'),
    url(r'^([a-zA-Z0-9]+)/([a-zA-Z0-9]+)$', views.zone_device_listing, name='dashboard-view-zone-type-devices'),
    url(r'^identify_device$', views.identify_device, name='dashboard-identify-device'),

]