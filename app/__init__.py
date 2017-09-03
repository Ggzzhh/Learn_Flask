#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

# 工厂函数
def create_app(config_name):
    # ...
    app = Flask(__name__)
    # 设置程序名为配置文件中的config字典中的值
    app.config.from_object(config[config_name])
    # 初始化app配置
    config[config_name].init_app(app)
    
    # 初始化各类拓展模块
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    
    # 附加路由和自定义的s错误页面
    from .main import main as main_blueprint
    # app的注册蓝本
    app.register_blueprint(main_blueprint,)
    
    return app