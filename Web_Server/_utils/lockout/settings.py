from django.conf import settings

MAX_ATTEMPTS = getattr(settings, 'LOCKOUT_MAX_ATTEMPTS', 3)
LOCKOUT_TIME = getattr(settings, 'LOCKOUT_TIME', 60 * 10) # 10 minutes
ENFORCEMENT_WINDOW = getattr(settings, 'LOCKOUT_ENFORCEMENT_WINDOW', 60 * 5) # 5 minutes
USE_USER_AGENT = getattr(settings, 'LOCKOUT_USE_USER_AGENT', False)
CACHE_PREFIX = getattr(settings, 'LOCKOUT_CACHE_PREFIX', 'lockout')