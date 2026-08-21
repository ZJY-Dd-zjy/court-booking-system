import sqlite3
import os

# 指向实际项目目录的数据库
DB_PATH = r'C:/Users/five_/PycharmProjects/FlaskProject/court_booking.db'

def clear_all():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        print("请确认路径是否正确")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"正在清理: {DB_PATH}")
    print("=" * 40)

    # 1. 清空所有预约记录
    cursor.execute("DELETE FROM reservations")
    print(f"预约记录已清空 (删除了 {cursor.rowcount} 条)")

    # 2. 清空所有用户（如果想保留账号，注释掉下面这行）
    cursor.execute("DELETE FROM users")
    print(f"用户账号已清空 (删除了 {cursor.rowcount} 条)")

    # 3. 把所有场地恢复为"空闲"
    cursor.execute("UPDATE courts SET status = '空闲'")
    print(f"所有场地已恢复为空闲状态")

    conn.commit()
    conn.close()

    print("=" * 40)
    print("✅ 清理完成！刷新浏览器页面即可看到变化")

if __name__ == '__main__':
    clear_all()
