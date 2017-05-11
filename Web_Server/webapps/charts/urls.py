from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'download_sheet/([a-zA-Z0-9]+)/$',views.export_time_series_data_spreadsheet, name='charts-export-data'),
    url(r'([a-zA-Z0-9]+)/$',views.charts_device, name='charts-view-device-chart')

]