# 清理 app.py 开头的调试代码和根路径的调试代码，改回5000端口
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 删除前两行 (import os 和 debug print)
if lines[0].strip() == 'import os' and '[DEBUG]' in lines[1]:
    lines = lines[2:]
    print('已删除开头调试代码')

# 检查第二行是否变成空行，如果是也删掉
if lines and lines[0].strip() == '':
    lines = lines[1:]

content = ''.join(lines)

# 清理根路径的调试代码
old_index = '''        "debug_file": os.path.abspath(__file__),
        "debug_db": db_path
    }, "场馆预约系统 API 已启动")'''

new_index = '''    }, "场馆预约系统 API 已启动")'''

content = content.replace(old_index, new_index)

# 改回5000端口
content = content.replace("app.run(host='0.0.0.0', debug=True, port=5001, use_reloader=False)", 
                          "app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=False)")

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# 同步桌面目录
with open(r'C:/Users/five_/Desktop/flaskproject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("清理完成：")
print("  - 删除开头 debug print")
print("  - 删除根路径 debug 字段")
print("  - 端口改回 5000")
