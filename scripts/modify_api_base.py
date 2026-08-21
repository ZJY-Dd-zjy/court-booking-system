import re

files = [
    r'C:\Users\five_\PycharmProjects\FlaskProject\login.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\courts.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\my.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\admin.html',
]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 在 <script> 标签后的第一个非空行插入 API_BASE
    # 找 <script> 后面第一个 var/let/const/function 或 fetch 之前的行
    # 简单方案：在第一个 <script> 标签后加变量声明
    script_tag = '<script>'
    idx = content.find(script_tag)
    if idx != -1:
        insert_pos = idx + len(script_tag)
        api_line = '\n        var API_BASE = "http://localhost:5000";  // 手机访问时改成你的电脑IP，如 http://192.168.1.105:5000\n'
        content = content[:insert_pos] + api_line + content[insert_pos:]

    # 替换 "http://localhost:5000 为 API_BASE + "
    content = content.replace('"http://localhost:5000', 'API_BASE + "')
    # 替换 'http://localhost:5000 为 API_BASE + '
    content = content.replace("'http://localhost:5000", "API_BASE + '")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'已修改: {path}')

print('\n全部完成！手机测试时，把 API_BASE 的 localhost 改成你的电脑IP即可。')
