#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
pagedown = PageDown()
# 用户回话安全等级 None basic strong
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = "请登录来访问这个页面"
login_manager.login_message_category = "info"

from .models import AnonymousUser
login_manager.anonymous_user = AnonymousUser


# 工厂函数
def create_app(config_name):
    # ...
    app = Flask(__name__)
    # 设置静态文件路径
    # app.static_url_path = "static"
    # 设置程序名为配置文件中的config字典中的值
    app.config.from_object(config[config_name])
    # 初始化app配置
    config[config_name].init_app(app)

    # 初始化各类拓展模块
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 把所有请求重定向到安全HTTP
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    # 附加路由和自定义的s错误页面
    from .main import main as main_blueprint
    # app的注册蓝本
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # url_prefix 是为所有的url加上的前缀
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册API蓝本 APP下的每个功能蓝本都在这里注册
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app