# -*- coding: utf-8 -*-
from django.core.urlresolvers import get_callable
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.core.cache import cache
import time
from .settings import THROTTLING,\
    THROTTLING_CACHE_PREFIX, \
    THROTTLING_CACHE_EXPIRE, \
    THROTTLING_CACHE_KEY_PATTERNS, \
    THROTTLING_ENABLED, \
    THROTTLING_IGNORE_ADMINS


def ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class Throttle(object):
    def __init__(self, request, view_func, view_args, view_kwargs):
        self.request = request
        self.view_func = view_func
        self.view_args = view_args,
        self.view_kwargs = view_kwargs
        self.view_name = '%s.%s' % (view_func.__module__, view_func.__name__)
        self.view_throttling = THROTTLING.get(self.view_name, {})
        self.method = request.method.lower()

    def get_cache_key(self):
        if 'uri' in self.view_throttling:
            if not self.request.path.startswith(self.view_throttling['uri']):
                return None, None

        timeouts = (
            ('view_method', self.view_throttling.get(self.method)),
            ('view', self.view_throttling.get('all')),
            ('site_method', THROTTLING.get(self.method)),
            ('site', THROTTLING.get('all')),
        )

        format_args = {
            'prefix': THROTTLING_CACHE_PREFIX,
            'view': self.view_name,
            'uid': self.request.user.id,
            'ip': ip(self.request),
            'method': self.request.method
        }

        if hasattr(self.request, 'session') and self.request.session.session_key:
            format_args['session'] = self.request.session.session_key

        for pattern_key, timeout in timeouts:
            if timeout is not None:
                if isinstance(timeout, basestring) and timeout.startswith('callable:'):
                    callback_name = timeout.split('callable:')[1]
                    return get_callable(callback_name)(self.request, self.view_func, self.view_args, self.view_kwargs)

                return THROTTLING_CACHE_KEY_PATTERNS[pattern_key] % format_args, timeout

        return None, None

    def check(self):
        if not THROTTLING_ENABLED:
            return

        if THROTTLING_IGNORE_ADMINS and self.request.user.is_superuser:
            return

        cache_key, timeout = self.get_cache_key()
        if not cache_key:
            return

        if timeout is False:  # view is disabled
            return HttpResponseBadRequest()

        if (timeout is None) or (timeout is 0):
            return

        if isinstance(timeout, basestring):
            if timeout.startswith('/'):
                return HttpResponseRedirect(timeout)
            else:
                callback = get_callable(timeout)
                maintenance_bundle = {
                    'view_func': self.view_func,
                    'view_args': self.view_args,
                    'view_kwargs': self.view_kwargs
                }

                return callback(self.request, maintenance_bundle)

        now = int(time.time() * 1000)
        last_access = cache.get(cache_key, 0)
        delta = now - last_access

        if delta >= timeout:
            cache.set(cache_key, now, THROTTLING_CACHE_EXPIRE)
            return

        congestion_view = self.view_throttling.get('congestion') or THROTTLING.get('congestion')
        if congestion_view:
            if congestion_view.startswith('/'):
                return HttpResponseRedirect(congestion_view)
            else:
                callback = get_callable(congestion_view)
                congestion_bundle = {
                    'view_func': self.view_func,
                    'view_args': self.view_args,
                    'view_kwargs': self.view_kwargs,
                    'timeout': timeout,
                    'delta': delta,
                }
                return callback(self.request, congestion_bundle)

        return HttpResponseBadRequest()