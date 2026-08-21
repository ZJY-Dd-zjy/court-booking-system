"""
===========================================
文件名: create_demo_db.py
作者: zjy / sbw
功能: 演示数据库初始化脚本
描述: 创建 court_booking.db，预置用户、场地和预约记录
      运行一次即可重置为演示状态
===========================================
"""
import sqlite3
import datetime
import os

# 使用与 app.py 相同的数据库路径
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'court_booking.db')

# 连接数据库（自动创建 court_booking.db）
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ========== 0. 清空旧数据（确保每次运行都是干净状态） ==========
cursor.execute('DROP TABLE IF EXISTS reservations')
cursor.execute('DROP TABLE IF EXISTS courts')
cursor.execute('DROP TABLE IF EXISTS users')
print("旧表已清空")

# ========== 1. 建表 ==========
# 用户表
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT DEFAULT '普通用户'
    )
''')

# 场地表
cursor.execute('''
    CREATE TABLE courts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        location TEXT,
        status TEXT DEFAULT '空闲'
    )
''')

# 预约表
cursor.execute('''
    CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        court_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        status TEXT DEFAULT '预约中',
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (court_id) REFERENCES courts(id)
    )
''')

print("三张表创建成功")

# ========== 2. 插入用户（12人） ==========
users = [
    ('zhangsan', '123456', '普通用户'),
    ('lisi', '123456', '普通用户'),
    ('wangwu', '123456', '普通用户'),
    ('zhaoliu', '123456', '普通用户'),
    ('sunqi', '123456', '普通用户'),
    ('zhouba', '123456', '普通用户'),
    ('wujiu', '123456', '普通用户'),
    ('zhengshi', '123456', '普通用户'),
    ('dongfang', '123456', '普通用户'),
    ('demo', 'demo', '普通用户'),     # <-- 演示专用账号
    ('admin', 'admin123', '管理员')
]
cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)
print(f"插入 {len(users)} 个用户")

# ========== 3. 插入场地（12个，类型多样） ==========
courts = [
    # 羽毛球
    ('A馆-羽毛球场 01', '羽毛球', '一楼A区', '空闲'),
    ('A馆-羽毛球场 02', '羽毛球', '一楼B区', '空闲'),
    ('A馆-羽毛球场 03', '羽毛球', '一楼C区', '空闲'),
    ('A馆-羽毛球场 04', '羽毛球', '一楼D区', '空闲'),
    # 乒乓球
    ('B馆-乒乓球场 01', '乒乓球', '二楼E区', '空闲'),
    ('B馆-乒乓球场 02', '乒乓球', '二楼F区', '空闲'),
    ('B馆-乒乓球场 03', '乒乓球', '二楼G区', '空闲'),
    # 篮球
    ('C馆-篮球场 01', '篮球', '三楼H区', '空闲'),
    ('C馆-篮球场 02', '篮球', '三楼I区', '空闲'),
    # 网球
    ('D馆-网球场 01', '网球', '四楼J区', '空闲'),
    ('D馆-网球场 02', '网球', '四楼K区', '空闲'),
    # 排球
    ('E馆-排球场 01', '排球', '五楼L区', '空闲')
]
cursor.executemany('INSERT INTO courts (name, type, location, status) VALUES (?, ?, ?, ?)', courts)
print(f"插入 {len(courts)} 个场地")

# ========== 4. 获取用户ID ==========
cursor.execute('SELECT id FROM users WHERE username = ?', ('zhangsan',))
zhangsan_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('lisi',))
lisi_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('wangwu',))
wangwu_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('zhaoliu',))
zhaoliu_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('sunqi',))
sunqi_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('zhouba',))
zhouba_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('wujiu',))
wujiu_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('zhengshi',))
zhengshi_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('dongfang',))
dongfang_id = cursor.fetchone()[0]
cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
demo_id = cursor.fetchone()[0]

# ========== 5. 获取场地ID ==========
cursor.execute('SELECT id FROM courts WHERE name = ?', ('A馆-羽毛球场 01',))
c1 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('A馆-羽毛球场 02',))
c2 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('A馆-羽毛球场 03',))
c3 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('A馆-羽毛球场 04',))
c4 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('B馆-乒乓球场 01',))
c5 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('B馆-乒乓球场 02',))
c6 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('B馆-乒乓球场 03',))
c7 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('C馆-篮球场 01',))
c8 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('C馆-篮球场 02',))
c9 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('D馆-网球场 01',))
c10 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('D馆-网球场 02',))
c11 = cursor.fetchone()[0]
cursor.execute('SELECT id FROM courts WHERE name = ?', ('E馆-排球场 01',))
c12 = cursor.fetchone()[0]

# ========== 6. 插入历史预约记录（每人2-3条） ==========
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

reservations = [
    # zhangsan - 偏好羽毛球
    (zhangsan_id, c1, '2026-08-10', '18:00', '20:00', '已使用', now),
    (zhangsan_id, c2, '2026-08-12', '19:00', '21:00', '已使用', now),
    (zhangsan_id, c3, '2026-08-14', '18:00', '20:00', '预约中', now),
    # lisi - 偏好乒乓球
    (lisi_id, c5, '2026-08-11', '19:00', '21:00', '已使用', now),
    (lisi_id, c6, '2026-08-13', '18:00', '20:00', '已使用', now),
    (lisi_id, c1, '2026-08-15', '20:00', '22:00', '预约中', now),
    # wangwu - 偏好篮球
    (wangwu_id, c8, '2026-08-10', '18:00', '20:00', '已使用', now),
    (wangwu_id, c9, '2026-08-12', '19:00', '21:00', '已使用', now),
    (wangwu_id, c8, '2026-08-16', '18:00', '20:00', '预约中', now),
    # zhaoliu - 偏好网球
    (zhaoliu_id, c10, '2026-08-11', '18:00', '20:00', '已使用', now),
    (zhaoliu_id, c11, '2026-08-13', '19:00', '21:00', '已使用', now),
    # sunqi - 偏好羽毛球
    (sunqi_id, c1, '2026-08-10', '19:00', '21:00', '已使用', now),
    (sunqi_id, c4, '2026-08-14', '18:00', '20:00', '预约中', now),
    # zhouba - 偏好乒乓球
    (zhouba_id, c5, '2026-08-11', '18:00', '20:00', '已使用', now),
    (zhouba_id, c7, '2026-08-15', '19:00', '21:00', '预约中', now),
    # wujiu - 偏好排球
    (wujiu_id, c12, '2026-08-12', '18:00', '20:00', '已使用', now),
    (wujiu_id, c12, '2026-08-16', '19:00', '21:00', '预约中', now),
    # zhengshi - 偏好篮球
    (zhengshi_id, c8, '2026-08-10', '20:00', '22:00', '已使用', now),
    (zhengshi_id, c9, '2026-08-14', '18:00', '20:00', '预约中', now),
    # dongfang - 偏好网球
    (dongfang_id, c10, '2026-08-13', '18:00', '20:00', '已使用', now),
    (dongfang_id, c11, '2026-08-15', '20:00', '22:00', '预约中', now),
    # demo - 偏好羽毛球（演示账号）
    (demo_id, c1, '2026-08-10', '18:00', '20:00', '已使用', now),
    (demo_id, c2, '2026-08-11', '18:00', '20:00', '已使用', now),
    (demo_id, c3, '2026-08-16', '19:00', '21:00', '预约中', now)
]
cursor.executemany('''
    INSERT INTO reservations (user_id, court_id, date, start_time, end_time, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', reservations)
print(f"插入 {len(reservations)} 条预约记录")

# ========== 7. 更新部分场地状态（有预约中的场地） ==========
occupied_courts = (c1, c3, c8, c12, c10)
cursor.execute("UPDATE courts SET status = '预约中' WHERE id IN (?, ?, ?, ?, ?)", occupied_courts)
print("更新场地状态")

# ========== 8. 提交并关闭 ==========
conn.commit()
conn.close()

print("\n court_booking.db 创建完成！")
print(f"   - 用户数: {len(users)}")
print(f"   - 场地数: {len(courts)}")
print(f"   - 预约数: {len(reservations)}")
print("\n演示账号: demo / demo")
print("管理员账号: admin / admin123")
