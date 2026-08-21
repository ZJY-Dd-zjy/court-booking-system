import os

path = r'C:\Users\five_\PycharmProjects\FlaskProject\app.py'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到插入位置（在 "场馆预约系统 API 已启动") 之后）
insert_idx = None
for i, line in enumerate(lines):
    if '场馆预约系统 API 已启动' in line:
        insert_idx = i + 1  # 插入到这一行之后
        break

if insert_idx is None:
    print("找不到插入位置")
    exit(1)

new_lines = [
    "\n",
    "\n",
    "# ---------- 2.7b 静态页面路由 ----------\n",
    "@app.route('/login.html')\n",
    "def serve_login():\n",
    "    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'login.html')\n",
    "\n",
    "@app.route('/courts.html')\n",
    "def serve_courts():\n",
    "    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'courts.html')\n",
    "\n",
    "@app.route('/my.html')\n",
    "def serve_my():\n",
    "    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'my.html')\n",
    "\n",
    "@app.route('/admin.html')\n",
    "def serve_admin():\n",
    "    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'admin.html')\n",
]

lines = lines[:insert_idx] + new_lines + lines[insert_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("已添加静态页面路由")
