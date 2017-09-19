# -*- coding: utf-8 -*-
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
    密码验证的回调函数
    如果不是匿名用户 且 密码为空 进行token验证
    如果有密码 进行密码验证
    """
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.fliter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """认证密令不正确 返回401错误"""
    return unauthorized('无效的参数')


# 在请求之前执行的功能
@api.before_request
@auth.login_required
def before_request():
    """在请求之前执行一次登陆验证 而且拒绝没有进行邮箱验证的用户访问"""
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('没有通过验证的用户')


@api.route('/token')
def get_token():
    """把认证令牌发送给客户端的路由"""
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('无效的参数')
    return jsonify({'token': g.current_user.genter_auth_token(
        expiration=3600), 'expiration': 3600})
