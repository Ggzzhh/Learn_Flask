# -*- coding: utf-8 -*-
# 导入Flask， 返回内容， 提供的模版
from flask import Flask, request, render_template
# 设置一个响应对象, 用户对话， 地址, flash
from flask import make_response, session, url_for, flash
# 重定向, abort终止（用于处理错误）
from flask import redirect, abort
# flask拓展 flask-script
from flask_script import Manager
# flask拓展 flask-bootstrap
from flask_bootstrap import Bootstrap
# flask拓展 flask-wtf
from flask_wtf import FlaskForm
# stringField 就是type=text的input  submit同理
from wtforms import StringField, SubmitField
# 导入验证器 的要求
from wtforms.validators import DataRequired

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
# 设置密匙
app.config['SECRET_KEY'] = '!(()(!$'

class NameForm(FlaskForm):
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('你的名字变成了' + form.name.data)
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/response')
def res():
    response = make_response('<h1>这个对象运输一个cookie！</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect/<id>')
def redirect_to_baidu(id):
    user = id
    if not user:
        abort(404)
    # return redirect('https://www.baidu.com')
    return id

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    manager.run()