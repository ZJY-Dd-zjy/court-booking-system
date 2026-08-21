import sqlite3
conn = sqlite3.connect(r'C:/Users/five_/PycharmProjects/FlaskProject/court_booking.db')
cursor = conn.cursor()

print('=== 用户数量 ===')
cursor.execute('SELECT COUNT(*) FROM users WHERE role=?', ('普通用户',))
print(f'普通用户: {cursor.fetchone()[0]}')
cursor.execute('SELECT id, username FROM users WHERE role=?', ('普通用户',))
for row in cursor.fetchall():
    print(f'  ID={row[0]}, {row[1]}')

print()
print('=== 预约数量 ===')
cursor.execute('SELECT COUNT(*) FROM reservations WHERE status IN (?,?)', ('预约中','已使用'))
print(f'有效预约: {cursor.fetchone()[0]}')

print()
print('=== 场地数量 ===')
cursor.execute('SELECT COUNT(*) FROM courts')
print(f'场地: {cursor.fetchone()[0]}')

conn.close()
