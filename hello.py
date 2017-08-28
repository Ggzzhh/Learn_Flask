# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
# 设置一个响应对象
from flask import make_response
# 重定向, abort终止（用于处理错误）
from flask import redirect, abort
# flask拓展 flask-script
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    # 获取首部user-agent（浏览器信息）
    # user_agent = request.headers.get('User-Agent')
    return render_template('index.html')

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


if __name__ == "__main__":
    manager.run()