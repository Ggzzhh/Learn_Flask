# -*- coding: utf-8 -*-
from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(permission):
    """防止未授权用户做某些操作的装饰器"""
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('没有足够的权限')
            return f(*args, **kwargs)
        return decorator_function
    return decorator
