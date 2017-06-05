# -*- coding: utf-8 -*-


# Create your views here.
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
from django.shortcuts import render
from bemoss_lib.communication.Email import EmailService
from django.db import transaction
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from _utils.lockout import LockedOut
from _utils.device_list_utils import get_device_list_and_count
from webapps.buildinginfos.models import Building_Zone
from webapps.multinode.models import NodeInfo, NodeDeviceStatus
from forms import RegistrationForm, RegistrationForm1
import logging
import _utils.messages as _
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from webapps.accounts.models import UserProfile, UserRegistrationRequests
from bemoss_lib.communication.Email import EmailService
import settings
emailservie = EmailService()
logger = logging.getLogger("views")

@ensure_csrf_cookie
def login_user(request):
    print "User login request"
    # Obtain the context for the user's request.
    context = RequestContext(request)

    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']
        user = None
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        try:
            user = authenticate(username=username, password=password)
        except LockedOut:
            messages.warning(request, 'Your account has been locked out because of too many failed login attempts.')

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                request.session['zipcode'] = '22204'
                logger.info("Login of user : %s", user.username)
                redirect_to = str(request.META.get('HTTP_REFERER', '/'))
                if redirect_to.__contains__('next='):
                    redirect_to = str(redirect_to).split('=')
                    redirect_to = redirect_to[1]
                    return HttpResponseRedirect(redirect_to)
                else:
                    return HttpResponseRedirect('/home/')
            else:
                # An inactive account was used - no logging in!
                messages.error(request, _.INACTIVE_USER)
                return HttpResponseRedirect('/login/')

        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            messages.error(request, _.INCORRECT_USER_PASSWORD)
            # return HttpResponse("Invalid login details supplied.")
            return HttpResponseRedirect('/login/')

    else:
        print request
        if request.user.is_authenticated():
            return HttpResponseRedirect('/home/')
        else:
            # The request is not a HTTP POST, so display the login form.
            # This scenario would most likely be a HTTP GET.
            return render(request,'accounts/login.html', {})


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required(login_url='/login/')
def logout_user(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/login/')

@ensure_csrf_cookie
def register(request):
    if request.method == "POST":
        form = RegistrationForm1(request.POST)

        if form.is_valid():
            if form["password1"].value() == form["password2"].value():
                kwargs = form.cleaned_data
                new_user = create_user(request, **kwargs)

                messages.success(request, "Thanks for creating an account!  Your login id is %s. "
                                          "Please wait for an email from BEMOSS admin for account activation." % kwargs[
                                     'username'])
                # return HttpResponseRedirect(reverse('registration_complete'))

                return HttpResponseRedirect('register')
            else:
                error = 'Passwords doesn\'t match, please try again.'
                messages.error(request, error)
                return HttpResponseRedirect('register')

        else:
            errors = json.dumps(form.errors)
            errors = json.loads(errors)
            for error in errors:
                print error
                message = ""
                for mesg in errors[error]:
                    message = message + "," + error + ":" + mesg
                message = message[:-1]
                message = message[1:]
                messages.error(request, message)

            return HttpResponseRedirect('register')

    else:
        form = RegistrationForm()
        context = RequestContext(request)
        return render(request,'accounts/registration_form.html', {})


@ensure_csrf_cookie
def forgotpassword_email(request):
    if request.method != "POST":
        return render(request,'accounts/forgot_password_email.html',{})

def reset_password(request):
    if request.method != "POST":
        return render(request,'accounts/reset_password.html',{})

def change_password(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        username = _data['id_user_name']
        password = _data['old_password']
        password_new = _data['id_password_new_1']
        try:
            u = User.objects.get(username=username)
        except:
            json_text = {
                "status": "failure1"
            }
            return HttpResponse(json.dumps(json_text), content_type='text/plain')
        user = authenticate(username=username, password=password)
        if user is not None:
            json_text = {
                "status": "success"
            }
            u.set_password(password_new)
            u.save()
            print "Password changed successfully"
        else:
            json_text = {
                "status": "failure2"
            }
        return HttpResponse(json.dumps(json_text), content_type='text/plain')  # This works

def email_password(request):
    if request.method == "POST":
        password = User.objects.make_random_password()
        _data = request.body
        _data = json.loads(_data)
        email = _data['id_email_']
        u = User.objects.get(email=email)
        u.set_password(password)
        u.save()
        emailService = EmailService()

        # email settings
        email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
        email_username = settings.NOTIFICATION['email']['username']
        email_password = settings.NOTIFICATION['email']['password']
        email_mailServer = settings.NOTIFICATION['email']['mailServer']
        emailService.sendEmail(email_fromaddr,email,email_username,email_password,_.EMAIL_USER_PASSWORD_CHANGE,
                              _.EMAIL_USER_PASSWORD_MESSAGE.format(u.username, password),email_mailServer,html=True)
        json_text = {
                "status": "success"
        }
        return HttpResponse(json.dumps(json_text), content_type='text/plain')

@transaction.atomic
def create_user(request, *args, **kwargs):
    new_user = User.objects.create_user(kwargs['username'], kwargs['email'], kwargs['password1'])
    new_user.save()
    new_user.is_active = False
    new_user.save()
    uuser = User.objects.get(username=kwargs['username'])
    uuser.first_name = kwargs['first_name']
    uuser.last_name = kwargs['last_name']
    uuser.save()
    return new_user


@login_required(login_url='/login/')
def user_manager(request):
    context = RequestContext(request)
    zones = Building_Zone.objects.all()
    device_list_side_nav = get_device_list_and_count(request)
    context.update(device_list_side_nav)

    if request.user.groups.filter(name='Admin').exists():
        _users = User.objects.all()
        groups = Group.objects.all()
        userprofiles = UserProfile.objects.all()
        data = {"users": _users, 'zones': zones, 'groups': groups, 'userprofiles':userprofiles}
        data.update(get_device_list_and_count(request))
        print _users
        return render(request,'accounts/user_manager.html', data)

    else:
        return HttpResponseRedirect('/home/')


@login_required(login_url='/login/')
def approve_users(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        print _data

        for row in _data['data']:
            user = User.objects.get(id=row[0])
            if row[1] == "true":
                user.is_active = True
            user_group = Group.objects.get(name=row[2].strip())
            if row[3].strip().lower() == 'all':
                user.userprofile.nodes.add(*NodeInfo.objects.all())
            else:
                user.userprofile.nodes.add(NodeInfo.objects.get(node_name=row[3].strip()))
            user.userprofile.save()
            user.groups.add(user_group)
            user.save()
            try:
                emailService = EmailService()
                email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
                email_username = settings.NOTIFICATION['email']['username']
                email_password = settings.NOTIFICATION['email']['password']
                email_mailServer = settings.NOTIFICATION['email']['mailServer']
                _email_subject=_.EMAIL_USER_APPROVED_SUBJECT
                recipient=[user.email]
                text=_.EMAIL_USER_MESSAGE
                new_text = text.format(user.first_name)
                emailService.sendEmail(email_fromaddr, recipient, email_username, email_password,
                                       _email_subject , new_text, email_mailServer, html=True)

            except Exception as er:
                print er

        print "user accounts activated"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')


@login_required(login_url='/login/')
def modify_user_permissions(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        print _data

        for row in _data['data']:
            user = User.objects.get(id=row[0].strip())
            if user.is_superuser:
                continue #ignore changes to super-user
            user_group = Group.objects.get(name=row[1].strip())
            nodes = row[2].strip().split()
            user.userprofile.nodes = [] #delete existing nodes
            for node in nodes:
                if node == 'all':
                    user.userprofile.nodes.add(*NodeInfo.objects.all())
                else:
                    user.userprofile.nodes.add(NodeInfo.objects.get(node_name=node))
            user.userprofile.save()
            user.groups = [] #delete existing group assignment
            user.groups.add(user_group)
            user.save()

        print "user accounts permissions modified"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')


@login_required(login_url='/login/')
def delete_user(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(_data)
        print _data

        user_id = _data['id']
        usr = User.objects.get(id=user_id)
        usr.delete()

        print "user account removed"
        json_text = {
            "status": "success"
        }

        return HttpResponse(json.dumps(json_text), content_type='text/plain')
