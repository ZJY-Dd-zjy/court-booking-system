"""
===========================================
文件名: sa_13.py
作者: zrd
功能: 算法演示配置 - 生成"优化前很差、优化后很好"的测试场景
描述: 提供演示数据生成、初始方案构造、匹配率计算和配置管理功能
===========================================
"""

import random
import json
from typing import List, Dict, Any, Tuple

DEMO_SCENARIOS = {
    "small": {
        "name": "小型演示 (8人, 3场地, 2时段)",
        "num_courts": 3,
        "num_users": 8,
        "num_time_slots": 2,
        "court_types": ["羽毛球", "乒乓球", "篮球"],
        "seed": 42,
        "expected_match_rate": 0.75,
        "description": "适合快速演示，优化前后对比明显"
    },
    "medium": {
        "name": "中型演示 (16人, 5场地, 3时段)",
        "num_courts": 5,
        "num_users": 16,
        "num_time_slots": 3,
        "court_types": ["羽毛球", "乒乓球", "篮球", "网球"],
        "seed": 123,
        "expected_match_rate": 0.70,
        "description": "更接近真实场景，效果显著"
    },
    "large": {
        "name": "大型演示 (30人, 8场地, 4时段)",
        "num_courts": 8,
        "num_users": 30,
        "num_time_slots": 4,
        "court_types": ["羽毛球", "乒乓球", "篮球", "网球", "足球"],
        "seed": 456,
        "expected_match_rate": 0.65,
        "description": "压力测试，验证算法可扩展性"
    }
}


def generate_demo_data(
        num_courts: int = 5,
        num_users: int = 16,
        num_time_slots: int = 2,
        court_types: List[str] = None,
        seed: int = 42,
        bad_initial_ratio: float = 0.8
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    生成带时间维度的演示数据

    关键设计：
    1. 每个用户有明确的偏好类型（1-2种）
    2. 初始分配方案故意设置得很差（大部分用户分配到不偏好的场地）
    3. 算法应该能显著改善匹配率

    Args:
        num_courts: 场地数量
        num_users: 用户数量
        num_time_slots: 每个场地的时间段数
        court_types: 场地类型列表
        seed: 随机种子
        bad_initial_ratio: 初始分配错误比例（0-1之间）

    Returns:
        (courts, users, time_slots) 用于算法输入
    """
    random.seed(seed)

    if court_types is None:
        court_types = ["羽毛球", "乒乓球", "篮球"]

    time_slots = []
    start_hour = 8
    slot_duration = 1.5
    for i in range(num_time_slots):
        start_time = start_hour + i * slot_duration
        end_time = start_time + slot_duration
        time_slots.append({
            "slot_id": i + 1,
            "date": "2026-08-16",
            "start_time": f"{int(start_time):02d}:{int((start_time % 1) * 60):02d}",
            "end_time": f"{int(end_time):02d}:{int((end_time % 1) * 60):02d}",
            "index": i
        })

    courts = []
    court_id = 1
    for i in range(num_courts):
        court_type = court_types[i % len(court_types)]
        location = f"{chr(65 + i % 5)}区"

        for slot in time_slots:
            courts.append({
                "id": court_id,
                "court_name": f"{court_type}场地{chr(65 + i)}",
                "type": court_type,
                "location": location,
                "slot_id": slot["slot_id"],
                "date": slot["date"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"],
                "time_index": slot["index"],
                "court_index": i,
                "unique_key": f"court_{i}_slot_{slot['slot_id']}"
            })
            court_id += 1

    users = []

    type_counts = {}
    for ct in court_types:
        type_counts[ct] = 0

    for i in range(num_users):
        num_prefs = random.choices([1, 2], weights=[0.4, 0.6])[0]

        if i < num_users * 0.6:
            preferred_types = court_types[:2]
            if num_prefs == 1:
                prefs = [random.choice(preferred_types)]
            else:
                prefs = preferred_types.copy()
        else:
            prefs = random.sample(court_types, min(num_prefs, len(court_types)))

        time_prefs = random.sample(
            [s["slot_id"] for s in time_slots],
            min(random.randint(1, min(2, len(time_slots))), len(time_slots))
        ) if len(time_slots) > 0 else []

        for p in prefs:
            if p in type_counts:
                type_counts[p] += 1

        users.append({
            "id": i + 1,
            "name": f"用户{i + 1}",
            "preference": prefs if len(prefs) > 1 else (prefs[0] if prefs else ""),
            "time_preferences": time_prefs,
            "level": random.choice(["初级", "中级", "高级"]),
            "priority": random.randint(1, 5)
        })

    return courts, users, time_slots


def create_bad_initial_plan(
        courts: List[Dict],
        users: List[Dict],
        time_slots: List[Dict],
        bad_ratio: float = 0.8
) -> List[Dict]:
    """
    创建一个故意很差的分配方案，用于演示对比

    Args:
        courts: 场地列表
        users: 用户列表
        time_slots: 时间段列表
        bad_ratio: 错误分配比例

    Returns:
        分配方案列表，每个元素包含 user_id, court_id, slot_id
    """
    plan = []
    num_users = len(users)
    num_court_slots = len(courts)

    users_with_prefs = []
    users_without_prefs = []

    for user in users:
        pref = user.get('preference', '')
        if pref:
            users_with_prefs.append(user)
        else:
            users_without_prefs.append(user)

    court_types = {}
    for court in courts:
        court_types[court['id']] = court.get('type', '')

    user_pref_types = {}
    for user in users:
        pref = user.get('preference', '')
        if isinstance(pref, list) and pref:
            user_pref_types[user['id']] = pref[0]
        elif isinstance(pref, str) and pref:
            user_pref_types[user['id']] = pref
        else:
            user_pref_types[user['id']] = None

    used_courts = set()
    court_slots = [c for c in courts]

    for user in users_with_prefs:
        user_id = user['id']
        pref_type = user_pref_types.get(user_id)

        if random.random() < bad_ratio and pref_type:
            wrong_courts = [c for c in court_slots if c['id'] not in used_courts
                            and c.get('type', '') != pref_type]
            if wrong_courts:
                court = random.choice(wrong_courts)
            else:
                available = [c for c in court_slots if c['id'] not in used_courts]
                court = random.choice(available) if available else random.choice(court_slots)
        else:
            matching_courts = [c for c in court_slots if c['id'] not in used_courts
                               and c.get('type', '') == pref_type]
            if matching_courts:
                court = random.choice(matching_courts)
            else:
                available = [c for c in court_slots if c['id'] not in used_courts]
                court = random.choice(available) if available else random.choice(court_slots)

        used_courts.add(court['id'])
        plan.append({
            'user_id': user_id,
            'user_name': user.get('name', f'用户{user_id}'),
            'court_id': court['id'],
            'court_name': court.get('court_name', ''),
            'court_type': court.get('type', ''),
            'slot_id': court.get('slot_id', 1),
            'start_time': court.get('start_time', ''),
            'end_time': court.get('end_time', ''),
            'preference': pref_type
        })

    for user in users_without_prefs:
        available = [c for c in court_slots if c['id'] not in used_courts]
        court = random.choice(available) if available else random.choice(court_slots)
        used_courts.add(court['id'])
        plan.append({
            'user_id': user['id'],
            'user_name': user.get('name', f"用户{user['id']}"),
            'court_id': court['id'],
            'court_name': court.get('court_name', ''),
            'court_type': court.get('type', ''),
            'slot_id': court.get('slot_id', 1),
            'start_time': court.get('start_time', ''),
            'end_time': court.get('end_time', ''),
            'preference': None
        })

    return plan


def calculate_plan_match_rate(
        plan: List[Dict],
        users: List[Dict]
) -> Dict[str, Any]:
    """
    计算一个分配方案的匹配率

    Args:
        plan: 分配方案
        users: 用户列表（包含偏好信息）

    Returns:
        匹配统计信息
    """
    user_prefs = {}
    for user in users:
        pref = user.get('preference', '')
        if isinstance(pref, list):
            user_prefs[user['id']] = pref
        elif isinstance(pref, str) and pref:
            user_prefs[user['id']] = [pref]
        else:
            user_prefs[user['id']] = []

    total = len(plan)
    matches = 0
    match_details = []

    for item in plan:
        user_id = item.get('user_id')
        court_type = item.get('court_type', '')
        user_pref_list = user_prefs.get(user_id, [])

        is_match = court_type in user_pref_list if user_pref_list else False
        if is_match:
            matches += 1
        match_details.append({
            'user_id': user_id,
            'user_name': item.get('user_name', ''),
            'court_type': court_type,
            'preference': user_pref_list,
            'is_match': is_match
        })

    return {
        'total': total,
        'matches': matches,
        'match_rate': matches / total if total > 0 else 0,
        'details': match_details
    }


def get_demo_config(scenario_name: str = "medium") -> Dict[str, Any]:
    """
    获取完整的演示配置

    Args:
        scenario_name: 场景名称，可选 'small', 'medium', 'large'

    Returns:
        包含数据、初始方案、预期结果的完整配置
    """
    if scenario_name not in DEMO_SCENARIOS:
        scenario_name = "medium"

    scenario = DEMO_SCENARIOS[scenario_name]

    courts, users, time_slots = generate_demo_data(
        num_courts=scenario['num_courts'],
        num_users=scenario['num_users'],
        num_time_slots=scenario['num_time_slots'],
        court_types=scenario['court_types'],
        seed=scenario['seed'],
        bad_initial_ratio=0.85
    )

    bad_plan = create_bad_initial_plan(
        courts, users, time_slots, bad_ratio=0.85
    )

    initial_stats = calculate_plan_match_rate(bad_plan, users)

    return {
        'scenario': scenario,
        'courts': courts,
        'users': users,
        'time_slots': time_slots,
        'bad_plan': bad_plan,
        'initial_stats': initial_stats,
        'expected_match_rate': scenario['expected_match_rate']
    }


def print_comparison(initial_stats: Dict, final_stats: Dict):
    """
    打印优化前后对比

    Args:
        initial_stats: 优化前统计
        final_stats: 优化后统计
    """
    improvement = final_stats['match_rate'] - initial_stats['match_rate']

    if improvement > 0.3:
        result_msg = "效果显著！匹配率提升了 {:.1%}".format(improvement)
    elif improvement > 0.15:
        result_msg = "效果明显！匹配率提升了 {:.1%}".format(improvement)
    else:
        result_msg = "效果一般，匹配率提升了 {:.1%}".format(improvement)

    return {
        'initial_matches': initial_stats['matches'],
        'final_matches': final_stats['matches'],
        'initial_rate': initial_stats['match_rate'],
        'final_rate': final_stats['match_rate'],
        'total': initial_stats['total'],
        'improvement': improvement,
        'message': result_msg
    }


def test_demo_config() -> bool:
    """
    测试演示配置

    Returns:
        所有测试是否通过
    """
    all_passed = True
    for name in ['small', 'medium', 'large']:
        config = get_demo_config(name)

        if config['initial_stats']['match_rate'] >= 0.4:
            all_passed = False
        if config['expected_match_rate'] <= 0.5:
            all_passed = False

    return all_passed


def get_demo_data_for_api(scenario_name: str = "medium") -> Dict[str, Any]:
    """
    获取用于 API 的演示数据

    返回格式与 /api/optimize 接口的输入格式兼容
    """
    config = get_demo_config(scenario_name)

    courts_api = []
    for court in config['courts']:
        courts_api.append({
            "id": court.get('id', 0),
            "name": court.get('court_name', ''),
            "type": court.get('type', ''),
            "location": court.get('location', '')
        })

    users_api = []
    for user in config['users']:
        pref = user.get('preference', '')
        if isinstance(pref, list):
            pref = pref[0] if pref else ''
        users_api.append({
            "id": user.get('id', 0),
            "username": user.get('name', ''),
            "preference": pref,
            "time_preferences": user.get('time_preferences', [])
        })

    return {
        "scenario": config['scenario']['name'],
        "courts": courts_api,
        "users": users_api,
        "time_slots": config['time_slots'],
        "bad_plan": config['bad_plan'],
        "initial_stats": config['initial_stats'],
        "expected_match_rate": config['expected_match_rate']
    }


if __name__ == "__main__":
    test_demo_config()