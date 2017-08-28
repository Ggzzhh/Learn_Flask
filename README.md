学习狗书产生的代码
================

Jinja2模版在html中的各种应用
--------------------------

* {{ 变量|过滤器 }}
    * 如  ```Hello, {{ name|capitalize }} ```把name变为首字母大写的方式展现出来

* 控制结构

    * 如 if-else 结构
        ```
        {% if user %}
            Hello, {{ user }}!
        {% else %}
            Hello, Stranger!
        {% endif %}
        ```

    * 如 for 循环结构
        ```
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
        ```

    * Jinja2 支持宏  宏是类似函数的存在 如：
        ```
        {%　macro render_comment(comment)　%} # macro就是宏
            <li>{{ comment }}</li>
        {% endmacro %}

        {% for comment in comments %}
            {{ macro.render_comment(comment) }}
        {% endfor %}
        ```