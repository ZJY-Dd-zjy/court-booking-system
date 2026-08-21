import sqlite3
import os
from datetime import datetime, timedelta
from datetime import datetime, timedelta

conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'court_booking.db'))
cursor = conn.cursor()

# ==================== 1. 添加 15 个新用户 ====================
new_users = [
    '羽毛球小王', '羽毛球小李', '羽毛球小张', '羽毛球小刘', '羽毛球小陈',
    '乒乓球小赵', '乒乓球小钱', '乒乓球小孙', '乒乓球小李2', '乒乓球小周',
    '篮球小吴', '篮球小郑', '篮球小王2', '篮球小冯', '篮球小褚'
]

user_ids = []
for username in new_users:
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f'用户 {username} 已存在，跳过')
        continue
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                   (username, '123456', '普通用户'))
    user_ids.append(cursor.lastrowid)

conn.commit()
print(f'新增用户: {len(user_ids)} 个，ID: {user_ids}')

# ==================== 2. 为每个用户创建预约 ====================
# 场地: 9=羽毛球01, 10=羽毛球02, 11=乒乓球01, 12=乒乓球02, 13=篮球01
# 前5个用户 → 羽毛球偏好
# 中间5个用户 → 乒乓球偏好
# 后5个用户 → 篮球偏好

base_date = datetime(2026, 8, 1)

# 预约计划: (user_id, court_id, date, start_time, end_time)
booking_plan = []

# 羽毛球组 (用户11-15)
for i, uid in enumerate(user_ids[0:5]):
    # 每人约3次，主要约羽毛球场
    booking_plan.append((uid, 9,  (base_date + timedelta(days=i)).strftime('%Y-%m-%d'), '18:00', '20:00'))
    booking_plan.append((uid, 10, (base_date + timedelta(days=i+1)).strftime('%Y-%m-%d'), '19:00', '21:00'))
    booking_plan.append((uid, 9,  (base_date + timedelta(days=i+2)).strftime('%Y-%m-%d'), '17:00', '19:00'))

# 乒乓球组 (用户16-20)
for i, uid in enumerate(user_ids[5:10]):
    booking_plan.append((uid, 11, (base_date + timedelta(days=i+3)).strftime('%Y-%m-%d'), '18:00', '20:00'))
    booking_plan.append((uid, 12, (base_date + timedelta(days=i+4)).strftime('%Y-%m-%d'), '19:00', '21:00'))
    booking_plan.append((uid, 11, (base_date + timedelta(days=i+5)).strftime('%Y-%m-%d'), '17:00', '19:00'))

# 篮球组 (用户21-25)
for i, uid in enumerate(user_ids[10:15]):
    booking_plan.append((uid, 13, (base_date + timedelta(days=i+6)).strftime('%Y-%m-%d'), '18:00', '20:00'))
    booking_plan.append((uid, 13, (base_date + timedelta(days=i+7)).strftime('%Y-%m-%d'), '19:00', '21:00'))
    booking_plan.append((uid, 13, (base_date + timedelta(days=i+8)).strftime('%Y-%m-%d'), '17:00', '19:00'))

# 清除旧预约冲突（先把这些用户的旧预约取消，避免重复）
for uid in user_ids:
    cursor.execute("UPDATE reservations SET status = '已取消' WHERE user_id = ? AND status = '预约中'", (uid,))

# 插入新预约（已使用/已超时状态，这样不影响当前场地占用，但能体现历史偏好）
inserted = 0
for uid, court_id, date, st, et in booking_plan:
    # 检查是否已存在相同预约
    cursor.execute('''
        SELECT id FROM reservations 
        WHERE user_id = ? AND court_id = ? AND date = ? AND start_time = ? AND end_time = ?
    ''', (uid, court_id, date, st, et))
    if cursor.fetchone():
        continue
    
    # 用 "已使用" 状态，这样不影响当前场地占用，但能统计到偏好
    cursor.execute('''
        INSERT INTO reservations (user_id, court_id, date, start_time, end_time, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
    ''', (uid, court_id, date, st, et, '已使用'))
    inserted += 1

conn.commit()
print(f'新增预约记录: {inserted} 条')

# ==================== 3. 验证结果 ====================
print('\n=== 验证：各用户偏好类型 ===')
for uid in user_ids:
    cursor.execute('''
        SELECT c.type, COUNT(*) as count
        FROM reservations r
        JOIN courts c ON r.court_id = c.id
        WHERE r.user_id = ? AND r.status != '已取消' AND r.status != '已超时'
        GROUP BY c.type ORDER BY count DESC LIMIT 1
    ''', (uid,))
    row = cursor.fetchone()
    cursor.execute('SELECT username FROM users WHERE id = ?', (uid,))
    name = cursor.fetchone()[0]
    pref = row[0] if row else '无'
    print(f'  {name} (ID={uid}): 偏好 {pref}')

conn.close()
print('\n✅ 完成！重启 Flask 后，admin.html 会显示真实用户和真实优化结果。')
