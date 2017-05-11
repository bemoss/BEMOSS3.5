from django.shortcuts import render

# Create your views here.


from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render

import logging

logger = logging.getLogger("views")


def login_user(request):
    print "inside login_user() method"
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

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
                return HttpResponseRedirect('/home/')
            else:
                # An inactive account was used - no logging in!
                messages.error(request, 'This account has been disabled by the administrator.')
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            messages.error(request, 'Your username/password information is incorrect.')
            # return HttpResponse("Invalid login details supplied.")
            return HttpResponseRedirect('/login/')
            # render_to_response('login/login.html', {}, context)

    else:
        # The request is not a HTTP POST, so display the login form.
        # This scenario would most likely be a HTTP GET.
        return render(request,'login/login.html', {})
