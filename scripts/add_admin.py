import sqlite3
import sys

def add_admin(username, password):
    """创建管理员账号"""
    conn = sqlite3.connect('court_booking.db')
    cursor = conn.cursor()
    
    # 检查用户名是否已存在
    cursor.execute('SELECT id, role FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        # 已存在，升级为管理员
        cursor.execute("UPDATE users SET role = '管理员' WHERE id = ?", (row[0],))
        conn.commit()
        print(f"用户 '{username}' 已升级为管理员！")
    else:
        # 新建管理员
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, '管理员')",
            (username, password)
        )
        conn.commit()
        print(f"管理员账号 '{username}' 创建成功！")
    
    # 显示所有用户
    print("\n当前所有用户：")
    print("-" * 40)
    cursor.execute('SELECT id, username, role FROM users')
    for r in cursor.fetchall():
        print(f"  ID:{r[0]} | {r[1]} | {r[2]}")
    
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        add_admin(sys.argv[1], sys.argv[2])
    else:
        # 默认创建一个 admin 账号
        add_admin('admin', 'admin123')
        print("\n默认管理员：用户名 admin，密码 admin123")
