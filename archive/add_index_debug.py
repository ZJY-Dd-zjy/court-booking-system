# 在根路径加入调试信息
with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_index = """    return success_response({
        "available_apis": [
            "/api/register",
            "/api/login",
            "/api/courts",
            "/api/book",
            "/api/cancel",
            "/api/checkin",
            "/api/my_reservations",
            "/api/recommend",
            "/api/users",
            "/api/optimize"
        ]
    }, "场馆预约系统 API 已启动")"""

new_index = """    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'court_booking.db')
    return success_response({
        "available_apis": [
            "/api/register",
            "/api/login",
            "/api/courts",
            "/api/book",
            "/api/cancel",
            "/api/checkin",
            "/api/my_reservations",
            "/api/recommend",
            "/api/users",
            "/api/optimize"
        ],
        "debug_file": os.path.abspath(__file__),
        "debug_db": db_path
    }, "场馆预约系统 API 已启动")"""

content = content.replace(old_index, new_index)

with open(r'C:/Users/five_/PycharmProjects/FlaskProject/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加调试信息到根路径")
