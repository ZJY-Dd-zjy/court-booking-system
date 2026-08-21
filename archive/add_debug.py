# 在 /api/users 返回中加入调试信息
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_return = """    conn.close()
    return success_response(result)"""

new_return = """    conn.close()
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    return success_response({
        'users': result,
        'debug_count': len(result),
        'debug_db_path': db_path,
        'debug_raw_users': len(users)
    })"""

content = content.replace(old_return, new_return)

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加调试信息")
