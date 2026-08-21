import os

files = [
    r'C:\Users\five_\PycharmProjects\FlaskProject\login.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\courts.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\my.html',
    r'C:\Users\five_\PycharmProjects\FlaskProject\admin.html',
]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修复错误的变量声明
    content = content.replace(
        'var API_BASE = API_BASE + "";  // 手机访问时改成你的电脑IP，如 http://192.168.1.105:5000',
        'var API_BASE = "http://localhost:5000";  // 手机访问时改成你的电脑IP，如 http://192.168.1.105:5000'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'已修复: {path}')

print('\n修复完成！')
