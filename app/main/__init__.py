#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""在本构造文件中定义蓝本"""
from flask import Blueprint
# 蓝本的名字是main 第二个参数是蓝本所在的包或者模块 大多数情况下使用__name__即可
main = Blueprint('main', __name__)
# 采用这个顺序是避免循环导入依赖
from . import views, errors
from ..models import Permission


# 上下文管理器 也可以叫做引用池
# 这样做即可避免在每次调用render_template()时都多添加一个模版参数
@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)
