'''
Created on 22 Jul 2011

@author: dgorissen
'''

from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
from django.utils.decorators import available_attrs
import hashlib

# simple token, unique per user and meant to be kept secret
def gen_token(user):
    h = hashlib.md5()
    h.update(user.username + user.password)
    return h.hexdigest()

# source: http://djangosnippets.org/snippets/2276/
def ratelimit(limit=10,length=86400):
    """ The length is in seconds and defaults to a day"""
    def decorator(func):
        def inner(request, *args, **kwargs):
            ip_hash = str(hash(request.META['REMOTE_ADDR']))
            result = cache.get(ip_hash)
            if result:
                result = int(result)
                if result == limit:
                    return HttpResponseForbidden("Ooops too many requests! You are limited to %s every %s seconds" %(limit,length))
                else:
                    result +=1
                    cache.set(ip_hash,result,length)
                    return func(request,*args,**kwargs)
            cache.add(ip_hash,1,length)
            return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)
    return decorator