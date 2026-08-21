"""
一键清空所有预约记录，恢复所有场地为"空闲"状态。
用法：python clear_reservations.py
"""
import sqlite3

def clear_all():
    conn = sqlite3.connect('court_booking.db')
    cursor = conn.cursor()

    # 删除所有预约记录（或改为全部已取消）
    cursor.execute("DELETE FROM reservations")
    print(f"已清空 {cursor.rowcount} 条预约记录")

    # 把所有场地状态恢复为空闲
    cursor.execute("UPDATE courts SET status = '空闲'")
    print(f"已恢复 {cursor.rowcount} 个场地为空闲状态")

    conn.commit()
    conn.close()
    print("✅ 全部场地已空闲，可以重新预约了")

if __name__ == '__main__':
    clear_all()
