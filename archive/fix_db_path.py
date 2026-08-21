# 修复 get_db() 为绝对路径
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_get_db = """def get_db():
    \"\"\"获取数据库连接，返回字典格式数据\"\"\"
    conn = sqlite3.connect('court_booking.db')
    conn.row_factory = sqlite3.Row
    return conn"""

new_get_db = """def get_db():
    \"\"\"获取数据库连接，返回字典格式数据\"\"\"
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn"""

content = content.replace(old_get_db, new_get_db)

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# 同步桌面目录
with open(r'C:/Users/five_/Desktop/flaskproject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("get_db() 已修复为绝对路径")
