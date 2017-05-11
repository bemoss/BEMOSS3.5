"""
Lockout Utils
"""
########################################################################

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from django.core.cache import cache
import settings
import re

########################################################################

WHITESPACE = re.compile('\s')

def generate_base_key(*params):
    """Generates a base key to be used for caching, containing the
    CACHE_PREFIX and the request ``params``, plus a hexdigest. The base key
    will later be combined with any required version or prefix.
    """    
    raw_key = ";".join(params)
    digest = md5(raw_key).hexdigest()
    
    # Whitespace is stripped but the hexdigest ensures uniqueness
    key = '%(prefix)s_%(raw_key)s_%(digest)s' % dict(
        prefix=settings.CACHE_PREFIX,
        raw_key=WHITESPACE.sub('', raw_key)[:125], 
        digest=digest)
    
    return key

########################################################################

def reset_attempts(request):
    """Clears the cache key for the specified ``request``.
    """
    params = []
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(', ')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    params.append(ip)
    if settings.USE_USER_AGENT:
        useragent = request.META.get('HTTP_USER_AGENT', '')
        params.append(useragent)
        
    key = generate_base_key(*params)
    cache.delete(key)
    
########################################################################