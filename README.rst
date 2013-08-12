``django-throttling`` is a an attempt at creating a simple app that allows to apply 
frequency limits to user's requests.

Features
========

* per-view maintenance mode
* per-view timeouts
* view disabling
* timeouts are configured with respect to ``request.method``
* redirects
* custom congestion views
* view timeouts support callbacks

Requirements
============

* django cache

Installation
============

Download ``django-throttling`` using *one* of the following methods:

pip
---

    pip install django-throttling

Checkout from GitHub
--------------------

Use one of the following commands::

    git clone http://github.com/night-crawler/django-throttling.git


Configuration
=============

Add 'django_throttling' into ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'django_throttling',
        ...
    )


MIDDLEWARE
----------

Add ``django_throttling.middleware.ThrottleMiddleware`` to your
``MIDDLEWARE_CLASSES`` in ``settings.py``. You may need 'request.user'
or 'request.session', etc., so insert it in a right place according to
your needs.


SETTINGS
--------

* ``DJANGO_THROTTLING_ENABLED``: enables 'django-throttling'. Default is ``False``.
* ``DJANGO_THROTTLING_CACHE_EXPIRE``: how long should we keep last_access time.
  If you set a large timeout for view, i.e. 24h, make sure that 
  ``DJANGO_THROTTLING_CACHE_EXPIRE`` is not less than your timeout.
  Default is ``60*60``
* ``DJANGO_THROTTLING_CACHE_PREFIX``: a cache prefix for keys. Default is
  ``THROTTLING``
* ``THROTTLING_CACHE_KEY_PATTERNS``: a dict with patterns for building the cache
  keys. May be redefined in app settings. Defaults are:

    * ``view_method``: cache key pattern for a view with a method specified. 
      Default pattern: ``%(prefix)s:%(view)s:%(uid)s:%(ip)s:%(method)s``
    * ``view``: cache key pattern for a view. Default pattern:
      ``%(prefix)s:%(view)s:%(uid)s:%(ip)s``
    * ``site_method``: cache key pattern for a whole site with a method.
      Default pattern: ``%(prefix)s:%(uid)s:%(ip)s:%(method)s``
    * ``site``: a global pattern. Default: ``%(prefix)s:%(uid)s:%(ip)s``

* ``DJANGO_THROTTLING_IGNORE_ADMINS``: ignore throttling if user is admin.
  Default is ``True``.
* ``DJANGO_THROTTLING``: a dict with app-path keys that configures the limits.
  I.e.:
  ``{'django.contrib.admin.options.change_view': {'all': 50, 'post': 5000}}``

See Usage. For more.

Usage
=====

Global fall-backs
-----------------

Fall-back timeouts setup for any request at the current site::

    DJANGO_THROTTLING = {
        'all': 1000,        
        'post': 10000,
        'congestion': 'forum.views.congestion',
    }


That stands for "one request per second, one POST request per 10s".
``congestion`` is a view called after the throttle check, if it failes.
It may be a ``uri``, i.e. ``/forum/congestion/``. Must uri start with '/'.

The simplest congestion view may look like::

    def congestion(request, congestion_bundle):
        user = request.user
        progress = int(float(congestion_bundle['delta']) / congestion_bundle['timeout'] * 100)
        c = Context({'user': user, 'congestion_bundle': congestion_bundle, 'progress': progress})
        return render_to_response(get_theme_template(user, 'congestion.html'), c,
            context_instance=RequestContext(request)
        )


``congestion_bundle`` is a dict, populated from a ``process_request()``::

    congestion_bundle = {
        'view_func': self.view_func,
        'view_args': self.view_args,
        'view_kwargs': self.view_kwargs,
        'timeout': timeout,
        'delta': delta,
    }


You may disable all ``POST``'s on your site ('maintenance mode')::

    DJANGO_THROTTLING = {
        'all': 1000,
        'post': False,
        'congestion': 'forum.views.congestion',
    }

In that case you will get `HttpResponseBadRequest()` on any POST.


Also, you may redirect your's `POST` users to an any page::

    DJANGO_THROTTLING = {
        'all': 1000,
        'post': '/',
        'congestion': 'forum.views.congestion',
    }


or you can use a custom maintenance view for it::


    DJANGO_THROTTLING = {
        'all': 1000,
        'post': 'forum.views.maintenance',
        'congestion': 'forum.views.congestion',
    }

Maintenance view may look like::

    def maintenance(request, maintenance_bundle):
        return HttpPreResponse(maintenance_bundle)



If you need a special cache key builder, or just to set a timeout is not enough
for you, you can use a callback for, i.e., `POST`, that have to make it's
checks and return a tuple of cache key and one of the supported timeout types::

    DJANGO_THROTTLING = {
        'all': 1000,
        'post': 'callable:helpers.trash.my_callback',
        'congestion': 'forum.views.congestion',
    }


And here's the example callback::

    def my_callback(request, view_func, view_args, view_kwargs):
        return 'some_strange_key_123', 10000

The full set of arguments the original view had is provided.


And don't forget, that it is a *fallback* section, that used *ONLY* if
you have no detailed rule for view throttling.


Per-view throttling
-------------------

Per-view throttling is almost the same::

    DJANGO_THROTTLING = {
        'all': 1000,
        'post': 'callable:helpers.trash.my_callback',
        'congestion': 'forum.views.congestion',

        'django.contrib.admin.options.change_view': {
            'post': False,            
            'all': 0,
            'uri': '/admin/forum/post/23/',
            # 'post': 'callable:helpers.trash.my_callback',
            # 'all': 4000,        
        },
    }


First, it will disable all limits for `django.contrib.admin.options.change_view`.
Then, it will disable the ``POST`` method for this view, **ONLY** if the
``request.path`` starts with '/admin/forum/post/23/'. Other options from
global setup are permitted.


