"""Web_Server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin

urlpatterns = [
url(r'^admin/', admin.site.urls),
url(r'',include('webapps.common.urls')),
url(r'^$',include('webapps.dashboard.urls')),
url(r'^home/',include('webapps.dashboard.urls')),
url(r'dashboard/',include('webapps.dashboard.urls')),
url(r'^accounts/',include('webapps.accounts.urls')),
url(r'^deviceinfos/',include('webapps.deviceinfos.urls')),
url(r'^discovery/',include('webapps.discovery.urls')),
url(r'^charts/',include('webapps.charts.urls')),
url(r'^buildinginfos/',include('webapps.buildinginfos.urls')),
url(r'^login/',include('webapps.login.urls')),
url(r'^multinode/',include('webapps.multinode.urls')),
url(r'^schedule/',include('webapps.schedule.urls')),
url(r'^application/',include('webapps.bemoss_applications.urls')),
url(r'^device/',include('webapps.device.urls')),
url(r'^alerts/',include('webapps.alerts.urls')),
url(r'^error/',include('webapps.error.urls')),


]
