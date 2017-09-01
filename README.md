学习狗书产生的代码以及笔记
=======================

Jinja2模版在html中的各种应用
--------------------------

* {{ 变量|过滤器 }}
    * 如  ```Hello, {{ name|capitalize }} ```把name变为首字母大写的方式展现出来

* 控制结构

    * 如 if-else 结构
        ```html
        {% if user %}
            Hello, {{ user }}!
        {% else %}
            Hello, Stranger!
        {% endif %}
        ```

    * 如 for 循环结构
        ```html
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
        ```

    * Jinja2 支持宏  宏是类似函数的存在 如：
        ```html
        {%　macro render_comment(comment)　%} # macro就是宏
            <li>{{ comment }}</li>
        {% endmacro %}

        {% for comment in comments %}
            {{ macro.render_comment(comment) }}
        {% endfor %}
        ```

    * 导入其他文件中存在的宏
        ```html
        {% import 'macros.html' as macros %}
        <ul>
            {% for comment in comments %}
                {{ macros.render_comment(comment) }}
            {% endfor %}
        </ul>
        # 导入整个文件
        {% include 'common.html' %}
        ```

    * 可以继承其他模版 比如头部信息或者导航等设置成一个基础模版 'base.html'
        * 例子参见templates/base.html 以及 index.html

    * flask拓展模块——flask-bootstrap
        * 基本用法参照例子templates/base.html
        * 如果要在已经有内容的块中添加新内容需要使用super()，如：
            ```html
            {% block scripts %}
            {{ super() }}
            <script type="text/javascript" src="my-script.js"></script>
            {% endblock %}
            ```

    * 自定义错误页面
        * py文件中写入以下内容（例）
            ```python
            @app.errorhandler(404)
            def page_not_found(e):
                return render_template('404.html'), 404

            @app.errorhandler(500)
            def internal_server_error(e):
                return render_template('500.html'), 500
            ```

        * 其余内容404.html在templates中

    * 连接 返回地址时 可使用函数url_for() 会返回相对地址 _external关键字参数默认为false
        ```html
        url_for('user', name='john', _external=True)
        #http://localhost:5000/user/john
        url_for('index', page=2) # /?page=2
        ```

    * 静态文件 比如css文件或者图片 例子是标签地址
        ```html
        {% block head %}
        {{ super() }}
        <link rel="shortcut icon" href="{{ url_for('static',
            filename = 'favicon.ico') }}" type='image/x-icon' />
        {% endblock %}
        ```

    * 时间渲染可使用flask拓展flask-moment模块 书中例子未实现


Web表单
-------
* 安装flask拓展--flask-wtf 处理表单

* 跨站请求伪造保护
        用app.config字典可以用来存储框架、拓展和程序本身的配置变量，这个对象还提供
    一些方法也可以从文件或者环境中导入配置量.

* 表单类
    示例代码参见hello.py
    * post提交后刷新页面浏览器会重新发送之前已经发送过的最后一个请求，所以最好的处理
    方式是让最后一个请求是get，也就是Post/重定向/Get模式.
    * 这个方式需要把post的请求内容存储起来 避免丢失 用session['内容']来存储在cookie中！

数据库
------
* 下载使用flask-SQLAlchemy管理数据库
    * 数据可参考python中文学习大本营 http://www.pythondoc.com/
    * 进度5.5
