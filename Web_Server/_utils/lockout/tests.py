"""
Lockout Tests
"""

########################################################################

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings
import settings as lockout_settings
from middleware import LockoutMiddleware
from exceptions import LockedOut
from utils import reset_attempts
import time

########################################################################

class LockoutTestCase(TestCase):
    """Test case for lockout functionality. Requires django.contrib.auth.
    """
    
    username = 'testlockoutuser'
    password = 'testpassword'
    badpassword = 'badpassword'
    ip1 = '64.147.222.137'
    ip2 = '168.212.226.204'
    useragent1 = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2'
    useragent2 = 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)'
    
    ####################################################################
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LockoutMiddleware()
        self.user = User.objects.create_user(
            self.username, 'testlockoutuser@email.com', self.password)
        self.badcredentials = dict(username=self.username, password=self.badpassword)
        self.goodcredentials = dict(username=self.username, password=self.password)
        
        self.MAX_ATTEMPTS_ORIG = lockout_settings.MAX_ATTEMPTS
        self.USE_USER_AGENT_ORIG = lockout_settings.USE_USER_AGENT
        self.LOCKOUT_TIME_ORIG = lockout_settings.LOCKOUT_TIME
        self.ENFORCEMENT_WINDOW_ORIG = lockout_settings.ENFORCEMENT_WINDOW
        lockout_settings.MAX_ATTEMPTS = 2
        lockout_settings.USE_USER_AGENT = True
        lockout_settings.LOCKOUT_TIME = 2
        lockout_settings.ENFORCEMENT_WINDOW = 3
    
    ####################################################################
    
    def tearDown(self):
        # Clear the lockout keys from the cache and restore lockout settings
        for ip in (self.ip1, self.ip2):
            for useragent in (self.useragent1, self.useragent2):
                request = self.factory.post(settings.LOGIN_URL, REMOTE_ADDR=ip, 
                                            HTTP_USER_AGENT=useragent)
                reset_attempts(request)
        
        lockout_settings.MAX_ATTEMPTS = self.MAX_ATTEMPTS_ORIG
        lockout_settings.USE_USER_AGENT = self.USE_USER_AGENT_ORIG
        lockout_settings.LOCKOUT_TIME = self.LOCKOUT_TIME_ORIG
        lockout_settings.ENFORCEMENT_WINDOW = self.ENFORCEMENT_WINDOW_ORIG
        
    
    ####################################################################
        
    def authenticate(self, request, **credentials):
        """Wraps auth.authenticate with LockoutMiddleware, since the
        tests do not trigger the middleware.
        """
        self.middleware.process_request(request)
        user = auth.authenticate(**credentials)
        self.middleware.process_response(None, None)
        return user
        
    ####################################################################
    
    def test_valid_login_allowed(self):
        """Sanity check that a valid login is not locked out.
        """
        request = self.factory.post(settings.LOGIN_URL, REMOTE_ADDR=self.ip1, 
                                    HTTP_USER_AGENT=self.useragent1)
        user = self.authenticate(request, **self.goodcredentials)
        self.assertEqual(user, self.user)
    
    ####################################################################
    
    def test_max_attempts(self):
        """Tests that the user is locked out after exceeding the max attempts.
        """
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
            
        request = self.factory.post(settings.LOGIN_URL, **meta)
        # User should be locked out even with a valid login.
        self.assertRaises(LockedOut, self.authenticate, request, **self.goodcredentials)
    
    ####################################################################
    
    def test_lockout_time(self):
        """Tests that the user is locked out for the appropriate length of time.
        """
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
           
        request = self.factory.post(settings.LOGIN_URL, **meta)
        self.assertRaises(LockedOut, self.authenticate, request, **self.badcredentials)
        
        # Let the lockout expire and retry.
        time.sleep(lockout_settings.LOCKOUT_TIME)
        
        request = self.factory.post(settings.LOGIN_URL, **meta)
        user = self.authenticate(request, **self.goodcredentials)
        self.assertEqual(user, self.user)
        
    ####################################################################
    
    def test_enforcement_window(self):
        """Tests that, after the enforcement window ends, the user gets a fresh start.
        """          
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        request = self.factory.post(settings.LOGIN_URL, **meta)
        user = self.authenticate(request, **self.badcredentials)
        
        # Let the enforcement window expire.
        time.sleep(lockout_settings.ENFORCEMENT_WINDOW)
        
        # The user is now allowed the max attempts without a lockout.
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
    
    ####################################################################
    
    def test_different_ips(self):
        """Tests that a lockout of one IP does not affect requests from a
        different IP.
        """
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
        
        # IP2 is not locked out...
        request = self.factory.post(settings.LOGIN_URL, REMOTE_ADDR=self.ip2, 
                                    HTTP_USER_AGENT=self.useragent1)
        user = self.authenticate(request, **self.goodcredentials)
        self.assertEqual(user, self.user)
        
        # ...even though IP1 is.
        request = self.factory.post(settings.LOGIN_URL, **meta)
        self.assertRaises(LockedOut, self.authenticate, request, **self.goodcredentials)
        
    ####################################################################
    
    def test_use_user_agent(self):
        """Tests that a user from the same IP but with a different user agent
        is not locked out, if USE_USER_AGENT is True.
        """
        self.assertTrue(lockout_settings.USE_USER_AGENT)
        
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
        
        # User agent 2 is not locked out...
        request = self.factory.post(settings.LOGIN_URL, REMOTE_ADDR=self.ip1, 
                                    HTTP_USER_AGENT=self.useragent2)
        user = self.authenticate(request, **self.goodcredentials)
        self.assertEqual(user, self.user)
        
        # ...even though user agent 1 is.
        request = self.factory.post(settings.LOGIN_URL, **meta)
        self.assertRaises(LockedOut, self.authenticate, request, **self.goodcredentials)
        
    ####################################################################
    
    def test_ignore_user_agent(self):
        """Tests that a user from the same IP but with a different user agent
        is locked out, if USE_USER_AGENT is False.
        """
        lockout_settings.USE_USER_AGENT = False
        
        meta = dict(REMOTE_ADDR=self.ip1, HTTP_USER_AGENT=self.useragent1)
        
        for i in range(lockout_settings.MAX_ATTEMPTS):
            request = self.factory.post(settings.LOGIN_URL, **meta)
            user = self.authenticate(request, **self.badcredentials)
        
        # User agent 2 from same IP is locked out
        request = self.factory.post(settings.LOGIN_URL, REMOTE_ADDR=self.ip1, 
                                    HTTP_USER_AGENT=self.useragent2)
        self.assertRaises(LockedOut, self.authenticate, request, **self.goodcredentials)
        
########################################################################