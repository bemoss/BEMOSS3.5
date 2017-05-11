from __future__ import unicode_literals

# Create your models here.
    # Copyright 2008-2010 Yousef Ourabi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

ABUSE_PREFIX = 'DJANGO_BANISH_ABUSE:'
BANISH_PREFIX = 'DJANGO_BANISH:'
WHITELIST_PREFIX = 'DJANGO_BANISH_WHITELIST:'


class Banishment(models.Model):

    # Flush out time constrained banned in future revisions
    # ban_start = models.DateField(help_text="Banish Start Date.")
    # ban_stop = models.DateField(help_text="Banish Stop Date.")
    # ban_is_permanent = models.BooleanField(help_text="Is Ban Permanent? (Start/Stop ignored)")

    ban_reason = models.CharField(max_length=255, help_text="Reason for the ban?")

    BAN_TYPES = (
        ('ip-address', 'IP Address'),
        ('user-agent', 'User Agent'),
    )

    type = models.CharField(
        max_length=20,
        choices=BAN_TYPES,
        default=0,
        help_text="Type of User Ban to store"
    )

    condition = models.CharField(
        max_length=255,
        help_text='Enter an IP to ban/whitelist, or a User Agent string to ban'
    )

    def __unicode__(self):
        return "Banished %s %s " % (self.type, self.condition)

    def __str__(self):
        return self.__unicode__()

    def is_current(self):
        """
        Determine if this banishment is current by comparing
        dates
        """
        if self.permanent or self.stop > datetime.date.today():
            return True
        return False

    class Meta:
        permissions = (("can_ban_user", "Can Ban User"),)
        verbose_name = "Banishment"
        verbose_name_plural = "Banishments"
        db_table = 'banishments'


class Whitelist(models.Model):
    whitelist_reason = models.CharField(max_length=255, help_text="Reason for the whitelist?")

    WHITELIST_TYPES = (
        ('ip-address-whitelist', 'Whitelist IP Address'),
    )

    type = models.CharField(
        max_length=20,
        choices=WHITELIST_TYPES,
        default=0,
        help_text='Enter an IP address to whitelist'
    )

    condition = models.CharField(
        max_length=255,
        help_text='Enter an IP to whitelist'
    )

    def __unicode__(self):
        return "Whitelisted %s %s " % (self.type, self.condition)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        permissions = (("can_whitelist_user", "Can Whitelist User"),)
        verbose_name = "Whitelist"
        verbose_name_plural = "Whitelists"
        db_table = 'whitelists'


def _generate_cache_key(instance):
    if instance.type == 'ip-address-whitelist':
         cache_key = WHITELIST_PREFIX + instance.condition
    if instance.type == 'ip-address':
         cache_key = BANISH_PREFIX + instance.condition
    abuse_key = ABUSE_PREFIX + instance.condition
    return cache_key, abuse_key


def _update_cache(sender, **kwargs):
    # add a whitelist entry and remove any abuse counter for an IP
    instance = kwargs.get('instance')
    cache_key, abuse_key = _generate_cache_key(instance)
    cache.set(cache_key, "1")
    cache.delete(abuse_key)


def _delete_cache(sender, **kwargs):
    instance = kwargs.get('instance')
    cache_key, abuse_key = _generate_cache_key(instance)
    cache.delete(cache_key)


post_save.connect(_update_cache, sender=Whitelist)
post_save.connect(_update_cache, sender=Banishment)
post_delete.connect(_delete_cache, sender=Whitelist)
post_delete.connect(_delete_cache, sender=Banishment)
