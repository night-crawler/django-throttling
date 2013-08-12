# -*- coding: utf-8 -*-
from .util import Throttle

class ThrottleMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        return Throttle(request, view_func, view_args, view_kwargs).check()
        #return throttle_check(request, view_func, view_args, view_kwargs)

