from django.conf.urls import url

from webapps.accounts import views

urlpatterns = [url(r'^$', views.login_user, name='login'),
]