from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^usr_mngr/?$', views.user_manager, name='account-user-manager'),
    url(r'^approve_users/$', views.approve_users, name='account-approve-users'),
    url(r'^modify_user_permissions/$', views.modify_user_permissions, name='account-modify-user-permissions'),
    url(r'^delete_user/$', views.delete_user, name='account-delete-user'),
    url(r'^login/?$', views.login_user, name='account-login'),
    url(r'^logout/?$',views.logout_user,name='account-logout'),
    url(r'^register/?$',views.register,name='account-register'),
    url(r'^forgotpassword_email/$',views.forgotpassword_email,name='account-forgot-password'),
    url(r'^resetpassword/?$',views.reset_password,name='account-reset-password'),
    url(r'^email_password/?$',views.email_password,name='account-email-password'),
    url(r'^change_password/?$',views.change_password,name='account-change-password'),
]
