"""
Lockout Middleware
"""

########################################################################

from threading import local
thread_namespace = local()

class LockoutMiddleware(object):
    """Decorates django.contrib.auth.authenticate with enforce_lockout, and
    adds the request to thread local so the decorator can access request
    details.
    """
    
    __state = {} # Borg pattern
    
    def __init__(self):
        self.__dict__ = self.__state
        self.installed = getattr(self, 'installed', False)
        if not self.installed:
            # Import here to avoid circular import.
            from decorators import enforce_lockout
            from django.contrib import auth
            auth.authenticate = enforce_lockout(auth.authenticate)
            self.installed = True

    ####################################################################
    
    def process_request(self, request):
        thread_namespace.lockoutrequest = request
        
    def process_response(self, request, response):
        # If a previous middleware returned a response or raised an exception,
        # our process_request won't have gotten called, so check before
        # deleting.
        if hasattr(thread_namespace, 'lockoutrequest'):
            delattr(thread_namespace, 'lockoutrequest')
        return response
        
########################################################################
