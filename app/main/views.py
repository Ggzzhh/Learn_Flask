#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""这个是视图路由，类似网站地图"""

from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    return render_template("index.html")


@main.route('/user/<username>')
def user(username):
    """该网页是用户资料页面"""
    web_user = User.query.filter_by(username=username).first_or_404()
    if web_user is None:
        abort(404)
    return render_template('user.html', user=web_user)


@main.route('/edit-profile', methods=["POST", "GET"])
@login_required
def edit_profile():
    """用户资料编辑页面"""
    form = EditProfileForm()
    print(1)
    if form.validate_on_submit():
        print(2)
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        print(3)
        db.session.add(current_user)
        print(4)
        flash("你的资料已经更改！")
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    print('这里')
    return render_template('edit_profile.html', form=form)




