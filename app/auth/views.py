# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationFrom
from ..email import send_email


# 使用钩子before_app_request过滤未确认用户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        # current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # 最好验证next的值不然会遭到重定向攻击
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("你已登出！")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationFrom()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        # 因为要用到id值 所以立刻提交以获取id
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认你的账户', 'auth/email/confirm', user=user,
                   token=token)
        flash("有一封确认邮件发送到了你的邮箱，请<b>登录</b>后完成邮箱认证！")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    # 查看用户的验证状态,如果为true 则去向首页
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 否则就进行验证
    if current_user.confirm(token):
        flash("完成验证，谢谢您的配合！")
    else:
        flash("验证无效或已过期，请重新验证邮箱！")
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认你的账户', 'auth/email/confirm',
               user=current_user,   token=token)
    flash("有一封确认邮件发送到了你的邮箱，请<b>登录</b>后完成邮箱认证！")
    return redirect(url_for('main.index'))

