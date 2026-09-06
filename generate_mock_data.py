"""
===========================================
文件名: generate_mock_data.py
作者: zjy / zrd
功能: 生成模拟的体育馆预约数据
描述: 用于神经网络训练和系统演示，数据分布基于常识
===========================================
"""

import json
import random
from datetime import datetime, timedelta

random.seed(42)

# ---------- 配置 ----------
NUM_USERS = 80           # 用户数
NUM_COURTS = 20          # 场地数（每种类型4-5个）
NUM_RECORDS = 500        # 历史预约记录数
DAYS = 30                # 模拟30天的数据

COURT_TYPES = ["羽毛球", "篮球", "乒乓球", "足球"]
LOCATIONS = ["A区一楼", "A区二楼", "B区一楼", "B区二楼", "C区一楼"]

# 时段配置
TIME_SLOTS = [
    {"id": 1, "start": "08:00", "end": "10:00", "hour": 8},
    {"id": 2, "start": "10:00", "end": "12:00", "hour": 10},
    {"id": 3, "start": "14:00", "end": "16:00", "hour": 14},
    {"id": 4, "start": "16:00", "end": "18:00", "hour": 16},
    {"id": 5, "start": "18:00", "end": "20:00", "hour": 18},  # 最热门
    {"id": 6, "start": "20:00", "end": "22:00", "hour": 20},  # 热门
]

# 偏好分布（基于常识）
TYPE_WEIGHTS = {"羽毛球": 0.35, "篮球": 0.25, "乒乓球": 0.25, "足球": 0.15}
SLOT_WEIGHTS = {1: 0.05, 2: 0.05, 3: 0.10, 4: 0.15, 5: 0.40, 6: 0.25}


def generate_users():
    """生成用户数据"""
    users = []
    for i in range(1, NUM_USERS + 1):
        # 用户偏好类型（加权随机）
        pref_type = random.choices(
            list(TYPE_WEIGHTS.keys()),
            weights=list(TYPE_WEIGHTS.values())
        )[0]
        
        # 偏好时段（加权随机，选1-2个）
        num_slots = random.choices([1, 2], weights=[0.6, 0.4])[0]
        time_prefs = random.choices(
            list(SLOT_WEIGHTS.keys()),
            weights=list(SLOT_WEIGHTS.values()),
            k=num_slots
        )
        
        users.append({
            "id": i,
            "username": f"user_{i:03d}",
            "preference": pref_type,
            "time_preferences": list(set(time_prefs)),  # 去重
            "level": random.choice(["初级", "中级", "高级"]),
            "priority": random.randint(1, 5)
        })
    return users


def generate_courts():
    """生成场地数据"""
    courts = []
    court_id = 1
    
    # 每种类型分配场地
    type_counts = {"羽毛球": 6, "篮球": 5, "乒乓球": 5, "足球": 4}
    
    for court_type, count in type_counts.items():
        for i in range(count):
            location = random.choice(LOCATIONS)
            courts.append({
                "id": court_id,
                "name": f"{court_type}场地{chr(65+i)}",
                "type": court_type,
                "location": location,
                "status": "空闲"
            })
            court_id += 1
    
    return courts


def generate_reservations(users, courts):
    """生成历史预约记录"""
    records = []
    
    # 记录每个场地-时段-日期的占用情况
    occupancy = {}  # key: (court_id, slot_id, date) -> user_id
    
    for _ in range(NUM_RECORDS):
        user = random.choice(users)
        
        # 用户倾向于选自己喜欢的类型
        if random.random() < 0.7:
            # 70%概率选偏好类型
            matching_courts = [c for c in courts if c["type"] == user["preference"]]
        else:
            # 30%概率随机选
            matching_courts = courts
        
        if not matching_courts:
            continue
        
        court = random.choice(matching_courts)
        
        # 时段选择：偏好时段概率更高
        if user["time_preferences"] and random.random() < 0.6:
            slot_id = random.choice(user["time_preferences"])
        else:
            slot_id = random.choices(
                list(SLOT_WEIGHTS.keys()),
                weights=list(SLOT_WEIGHTS.values())
            )[0]
        
        # 随机日期
        day_offset = random.randint(0, DAYS - 1)
        date = (datetime(2026, 8, 1) + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        
        # 检查冲突
        key = (court["id"], slot_id, date)
        if key in occupancy:
            # 冲突了，记录为"已取消"或跳过
            if random.random() < 0.3:
                records.append({
                    "id": len(records) + 1,
                    "user_id": user["id"],
                    "court_id": court["id"],
                    "date": date,
                    "slot_id": slot_id,
                    "status": "已取消",
                    "reason": "场地冲突"
                })
            continue
        
        occupancy[key] = user["id"]
        
        # 状态分布
        status = random.choices(
            ["已使用", "已取消", "已超时"],
            weights=[0.75, 0.15, 0.10]
        )[0]
        
        records.append({
            "id": len(records) + 1,
            "user_id": user["id"],
            "court_id": court["id"],
            "date": date,
            "slot_id": slot_id,
            "status": status,
            "created_at": f"{date} {random.choice(['08:00', '12:00', '17:00'])}"
        })
    
    return records


def generate_summary(users, courts, records):
    """生成数据摘要"""
    type_dist = {}
    slot_dist = {}
    status_dist = {}
    
    for r in records:
        t = courts[r["court_id"] - 1]["type"]
        type_dist[t] = type_dist.get(t, 0) + 1
        
        s = r["slot_id"]
        slot_dist[s] = slot_dist.get(s, 0) + 1
        
        st = r["status"]
        status_dist[st] = status_dist.get(st, 0) + 1
    
    return {
        "总用户数": len(users),
        "总场地数": len(courts),
        "总记录数": len(records),
        "类型分布": type_dist,
        "时段分布": slot_dist,
        "状态分布": status_dist
    }


def main():
    print("=" * 50)
    print("生成模拟体育馆预约数据")
    print("=" * 50)
    
    users = generate_users()
    courts = generate_courts()
    records = generate_reservations(users, courts)
    
    # 保存数据
    data = {
        "users": users,
        "courts": courts,
        "reservations": records,
        "time_slots": TIME_SLOTS,
        "summary": generate_summary(users, courts, records)
    }
    
    with open("mock_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到 mock_data.json")
    print(f"\n数据摘要:")
    for k, v in data["summary"].items():
        print(f"  {k}: {v}")
    
    # 同时生成CSV版本（方便Excel查看）
    import csv
    with open("mock_reservations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "user_id", "court_id", "date", "slot_id", "status"])
        writer.writeheader()
        for r in records:
            writer.writerow({k: r[k] for k in ["id", "user_id", "court_id", "date", "slot_id", "status"]})
    
    print(f"\n✅ CSV已保存到 mock_reservations.csv")


if __name__ == "__main__":
    main()
