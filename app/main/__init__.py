#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""在本构造文件中定义蓝本"""
from flask import Blueprint
# 蓝本的名字是main 第二个参数是蓝本所在的包或者模块 大多数情况下使用__name__即可
main = Blueprint('main', __name__)
# 采用这个顺序是避免循环导入依赖
from . import views, errors