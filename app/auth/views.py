# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationFrom, ResetForm, ResetFormRequest
from .forms import ChangePasswordForm, ChangeEmailForm
from ..email import send_email


# 使用钩子before_app_request过滤未确认用户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
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


@auth.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    """重置密码"""
    # 如果不是普通用户 就重定向到首页
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_email(user.email, '重置密码', 'auth/email/reset_password',
                       user=user, token=token)
            flash("有一封确认邮件发送到了你的邮箱，请去邮箱查看并完成密码重置！")
            return redirect(url_for('auth.login'))
        flash("邮箱错误！请重新输入！")
        form.email.data = ""
        return redirect(url_for('auth.reset_password'))
    return render_template('auth/reset_password.html', form=form)
    

@auth.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password_request(token):
    """重置密码 写入数据库"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetFormRequest()
    if form.validate_on_submit():
        id = User.my_get_id(token)
        user = User.query.filter_by(id=id).first()
        if user:
            user.password = form.password.data
            db.session.add(user)
            flash("你的密码已经修改！请登录！")
            return redirect(url_for('auth.login', token=token, _external=True))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_passowrd_request.html', form=form)


@auth.route('/change_password', methods=["GET", "POST"])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash("您输入的旧密码错误！请重新输入！")
            return redirect(url_for('auth.change_password'))
        current_user.password = form.password.data
        db.session.add(current_user)
        flash("你的密码已经修改！请重新登录！")
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/change_email', methods=["GET" ,"POST"])
@login_required
def change_email_request():
    """请求更改邮箱"""
    form = ChangeEmailForm()
    new_email = form.new_email.data
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            flash("您输入的密码错误！请重新输入！")
            return redirect(url_for('auth.change_email_request'))
        token = current_user.generate_email_change_token(new_email)
        send_email(new_email, "更换登录邮箱", "auth/email/change_email",
                   user=current_user, token=token)
        logout_user()
        flash("一封验证邮件已经发送到你的新邮箱！请完成验证并重新登录！")
        return redirect(url_for('auth.login'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    """在数据库内更改邮箱"""
    if current_user.change_email(token):
        flash("你的邮箱已经更改！请重新登录！")
        return redirect(url_for('auth.login'))
    else:
        flash("无效的请求！")
    return redirect(url_for('main.index'))