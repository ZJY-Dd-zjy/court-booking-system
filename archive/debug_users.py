# 验证：直接查数据库 vs API 返回
import sqlite3
import json

# 1. 直接查数据库
conn = sqlite3.connect(r'C:/Users/five_/PycharmProjects/FlaskProject/court_booking.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== 直接查数据库 ===')
cursor.execute('SELECT id, username, role FROM users WHERE role=?', ('普通用户',))
users_db = cursor.fetchall()
print(f'普通用户数量: {len(users_db)}')
for u in users_db:
    print(f'  ID={u["id"]}, {u["username"]}')

# 2. 检查 /api/users 查询的 SQL 是否有问题
print('\n=== 模拟 /api/users 查询 ===')
cursor.execute('SELECT id, username, role FROM users WHERE role = ?', ('普通用户',))
users = cursor.fetchall()
result = []
for user in users:
    cursor.execute('''
        SELECT c.type, COUNT(*) as count
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
        GROUP BY c.type ORDER BY count DESC LIMIT 1
    ''', (user['id'],))
    pref_row = cursor.fetchone()
    preference = pref_row['type'] if pref_row else '羽毛球'
    result.append({'id': user['id'], 'username': user['username'], 'preference': preference})

print(f'结果数量: {len(result)}')
for r in result:
    print(f'  {r}')

conn.close()
