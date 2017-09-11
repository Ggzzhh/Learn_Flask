# -*- coding: utf-8 -*-
"""本脚本专门用于写装饰器"""

from functools import wraps
from flask import abort
from flask_login import current_user

from .models import Permission


def permission_required(permission):
    """这是个装饰器，作用是：检查必须具有的权限"""
    def decorator(func):
        # @wraps()装饰器的作用是保存传入的对象功能、名字保持不变
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                # abort(403) 会停止程序并弹回一个403错误页面
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    """这个装饰器检查是否是管理员"""
    return permission_required(Permission.ADMINISTER)(func)
