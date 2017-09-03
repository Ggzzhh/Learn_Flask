#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""这个是视图路由，类似网站地图"""

from datetime import datetime
from flask import render_template, session, redirect, url_for

from . import main
from .forms import NameForm
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    form = NameForm()
    # 如果提交了表单
    if form.validate_on_submit():
        # 查询数据库中是否有该用户
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = '请输入姓名？？？'
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

