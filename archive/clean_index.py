# 清理 index() 中残留的调试代码
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_debug = '''    """根路径，返回可用接口列表"""
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    return success_response({'''

new_clean = '''    """根路径，返回可用接口列表"""
    return success_response({'''

content = content.replace(old_debug, new_clean)

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

# 同步桌面
with open(r'C:/Users/five_/Desktop/flaskproject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已清理 index() 中的调试代码")
