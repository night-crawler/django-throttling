# -*- coding: utf-8 -*-
from django.conf import settings

THROTTLING_ENABLED = getattr(settings, 'DJANGO_THROTTLING_ENABLED', False)
THROTTLING_CACHE_EXPIRE = getattr(settings, 'DJANGO_THROTTLING_CACHE_EXPIRE', 60*60)
THROTTLING_CACHE_PREFIX = getattr(settings, 'DJANGO_THROTTLING_CACHE_PREFIX', 'THROTTLING')

THROTTLING = getattr(settings, 'DJANGO_THROTTLING', {})

THROTTLING_CACHE_KEY_PATTERNS = getattr(settings, 'DJANGO_THROTTLING_CACHE_KEY_PATTERNS', {
    'view_method': "%(prefix)s:%(view)s:%(uid)s:%(ip)s:%(method)s",
    'view': "%(prefix)s:%(view)s:%(uid)s:%(ip)s",

    'site_method': "%(prefix)s:%(uid)s:%(ip)s:%(method)s",
    'site': "%(prefix)s:%(uid)s:%(ip)s",
})

THROTTLING_IGNORE_ADMINS = getattr(settings, 'DJANGO_THROTTLING_IGNORE_ADMINS', True)