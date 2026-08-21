# 清理 /api/users 中的调试代码，恢复为正常返回
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_debug = """    conn.close()
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    return success_response({
        'users': result,
        'debug_count': len(result),
        'debug_db_path': db_path,
        'debug_raw_users': len(users)
    })"""

new_clean = """    conn.close()
    return success_response(result)"""

content = content.replace(old_debug, new_clean)

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("调试代码已清理")
