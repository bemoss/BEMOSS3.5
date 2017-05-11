# Copyright 2008-2013 Yousef Ourabi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys

import django
from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.exceptions import MiddlewareNotUsed
from django.core.cache import cache

from models import Banishment, Whitelist


class BanishMiddleware(object):
    def __init__(self):
        """
        Middleware init is called once per server on startup - do the heavy
        lifting here.
        """
        # If disabled or not enabled raise MiddleWareNotUsed so django
        # processes next middleware.
        self.ENABLED = getattr(settings, 'BANISH_ENABLED', False)
        self.DEBUG = getattr(settings, 'BANISH_DEBUG', False)
        self.ABUSE_THRESHOLD = getattr(settings, 'BANISH_ABUSE_THRESHOLD', 75)
        self.USE_HTTP_X_FORWARDED_FOR = getattr(settings, 'BANISH_USE_HTTP_X_FORWARDED_FOR', False)
        self.BANISH_EMPTY_UA = getattr(settings, 'BANISH_EMPTY_UA', True)
        self.BANISH_MESSAGE = getattr(settings, 'BANISH_MESSAGE', 'You are banned.')

        if not self.ENABLED:
            raise MiddlewareNotUsed(
                "DoS Secure is not enabled via settings.py")

        if self.DEBUG:
            print >> sys.stderr, "[dos_secure] status = enabled"

        # Prefix All keys in cache to avoid key collisions
        self.BANISH_PREFIX = 'DJANGO_BANISH:'
        self.ABUSE_PREFIX = 'DJANGO_BANISH_ABUSE:'
        self.WHITELIST_PREFIX = 'DJANGO_BANISH_WHITELIST:'

        self.BANNED_AGENTS = []

        if self.BANISH_EMPTY_UA:
            self.BANNED_AGENTS.append(None)

        # Populate various 'block' buckets
        for ban in Banishment.objects.all():
            if self.DEBUG:
                print >> sys.stderr, "IP BANISHMENT: ", ban.type

            if ban.type == 'ip-address':
                cache_key = self.BANISH_PREFIX + ban.condition
                cache.set(cache_key, "1")

            if ban.type == 'user-agent':
                self.BANNED_AGENTS.append(ban.condition)
 
        for whitelist in Whitelist.objects.all():
            if whitelist.type == 'ip-address-whitelist':
                cache_key = self.WHITELIST_PREFIX + whitelist.condition
                cache.set(cache_key, "1")

    def _get_ip(self, request):
        ip = request.META['REMOTE_ADDR']
        if self.USE_HTTP_X_FORWARDED_FOR or not ip or ip == '127.0.0.1':
            ip = request.META.get('HTTP_X_FORWARDED_FOR', ip).split(',')[0].strip()
        return ip

    def process_request(self, request):
        ip = self._get_ip(request)

        user_agent = request.META.get('HTTP_USER_AGENT', None)

        if self.DEBUG:
            print >> sys.stderr, "GOT IP FROM Request: %s and User Agent %s" % (ip, user_agent)

        # Check whitelist first, if not allowed, then check ban conditions
        if self.is_whitelisted(ip):
          return None
        elif self.is_banned(ip) or self.monitor_abuse(ip) or user_agent in self.BANNED_AGENTS:
            return self.http_response_forbidden(self.BANISH_MESSAGE, content_type="text/html")

    def http_response_forbidden(self, message, content_type):
        if django.VERSION[:2] > (1,3):
            kwargs = {'content_type': content_type}
        else:
            kwargs = {'mimetype': content_type}
        return HttpResponseForbidden(message, **kwargs)

    def is_banned(self, ip):
        # If a key BANISH MC key exists we know the user is banned.
        is_banned = cache.get(self.BANISH_PREFIX + ip)
        if self.DEBUG and is_banned:
            print >> sys.stderr, "BANISH BANNED IP: ", self.BANISH_PREFIX + ip
        return is_banned

    def is_whitelisted(self, ip):
        # If a whitelist key exists, return True to allow the request through
        is_whitelisted = cache.get(self.WHITELIST_PREFIX + ip)
        if self.DEBUG and is_whitelisted:
            print >> sys.stderr, "BANISH WHITELISTED IP: ", self.WHITELIST_PREFIX + ip
        return is_whitelisted

    def monitor_abuse(self, ip):
        """
        Track the number of hits per second for a given IP.
        If the count is over ABUSE_THRESHOLD block user
        """
        cache_key = self.ABUSE_PREFIX + ip
        abuse_count = cache.get(cache_key)
        if self.DEBUG:
            print >> sys.stderr, "BANISH ABUSE COUNT: ", abuse_count
            print >> sys.stderr, "BANISH CACHE KEY: ", cache_key

        over_abuse_limit = False

        if not abuse_count:
            cache.set(cache_key, 1, 60)
        else:
            if abuse_count >= self.ABUSE_THRESHOLD:
                over_abuse_limit = True
                # Store IP Abuse in memcache and database
                ban = Banishment(
                    ban_reason="IP Abuse limit exceeded",
                    type="ip-address",
                    condition=ip,
                )
                ban.save()
                cache.set(self.BANISH_PREFIX + ip, "1")

            cache.incr(cache_key)
        return over_abuse_limit
