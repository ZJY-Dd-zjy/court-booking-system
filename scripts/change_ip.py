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

    content = content.replace('http://localhost:5000', 'http://192.168.1.41:5000')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'已修改: {path}')

print('\n全部完成！')
