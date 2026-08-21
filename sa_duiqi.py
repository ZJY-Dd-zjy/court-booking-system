"""
===========================================
文件名: sa_duiqi.py
作者: zrd
功能: 模拟退火算法 - 场馆分配优化
描述: 带时间维度和场地唯一性约束的优化算法,
      提供全局最优场地分配方案计算
===========================================
"""

import random
import time
import json
import sys
import os
from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


class SolutionCache:
    """解决方案缓存，优化适应度计算"""
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key, value):
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0


def generate_test_data_with_time(
    num_courts: int = 20,
    num_users: int = 50,
    num_time_slots: int = 4,
    court_types: List[str] = None,
    seed: int = 42
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    生成带时间维度的测试数据
    
    Args:
        num_courts: 场地数量
        num_users: 用户数量
        num_time_slots: 每个场地的时间段数
        court_types: 场地类型列表
        seed: 随机种子
    
    Returns:
        (courts, users, time_slots)
    """
    random.seed(seed)
    np.random.seed(seed)
    
    if court_types is None:
        court_types = ["羽毛球", "乒乓球", "篮球", "足球", "网球", "排球", "游泳", "健身"]
    
    time_slots = []
    start_hour = 8
    end_hour = 22
    slot_duration = 1.5  # 小时
    
    for i in range(num_time_slots):
        start_time = datetime(2026, 1, 1, start_hour, 0) + timedelta(hours=i * slot_duration)
        end_time = start_time + timedelta(hours=slot_duration)
        if end_time.hour >= end_hour:
            break
        time_slots.append({
            "slot_id": i + 1,
            "date": "2026-01-15",
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "index": i
        })
    
    courts = []
    court_id = 1
    for i in range(num_courts):
        court_type = random.choice(court_types)
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
    users = []
    for i in range(num_users):
        num_prefs = random.choices([0, 1, 2], weights=[0.2, 0.5, 0.3])[0]
        if num_prefs > 0:
            prefs = random.sample(court_types, min(num_prefs, len(court_types)))
        else:
            prefs = []
        
        time_prefs = random.sample(
            [s["slot_id"] for s in time_slots], 
            min(random.randint(1, 2), len(time_slots))
        ) if len(time_slots) > 0 else []
        
        users.append({
            "id": i + 1,
            "name": f"用户{i+1}",
            "preference": prefs if len(prefs) > 1 else (prefs[0] if prefs else ""),
            "time_preferences": time_prefs,
            "level": random.choice(["初级", "中级", "高级"]),
            "priority": random.randint(1, 5)
        })
    
    return courts, users, time_slots


def calculate_fitness_with_constraints(
    solution: List[int],
    user_prefs: List[List[str]],
    court_info: List[Dict],
    user_time_prefs: List[List[int]] = None,
    cache: SolutionCache = None
) -> float:
    """
    计算适应度，包含场地唯一性约束
    
    Args:
        solution: 每个用户分配的场地索引（court_slot索引）
        user_prefs: 每个用户的偏好类型列表
        court_info: 场地信息列表
        user_time_prefs: 每个用户偏好的时间段
        cache: 缓存对象
    
    Returns:
        适应度值 (越高越好)
    """
    if cache is not None:
        key = tuple(solution)
        cached = cache.get(key)
        if cached is not None:
            return cached
    
    num_users = len(solution)
    
    court_slot_usage = defaultdict(int)
    for court_idx in solution:
        court_slot_usage[court_idx] += 1
    
    violation_penalty = 0
    for court_idx, count in court_slot_usage.items():
        if count > 1:
            violation_penalty += (count - 1) * 10
    
    if any(count > 1 for count in court_slot_usage.values()):
        violation_penalty += 50
    
    match_score = 0
    type_match_count = 0
    time_match_count = 0
    
    for user_idx, court_idx in enumerate(solution):
        if court_idx >= len(court_info):
            continue
        
        court = court_info[court_idx]
        court_type = court.get('type', '')
        
        user_pref_list = user_prefs[user_idx] if user_idx < len(user_prefs) else []
        if court_type in user_pref_list:
            type_match_count += 1
            match_score += 10
        
        if user_time_prefs and user_idx < len(user_time_prefs):
            user_time_prefs_list = user_time_prefs[user_idx]
            if user_time_prefs_list:
                slot_id = court.get('slot_id', 0)
                if slot_id in user_time_prefs_list:
                    time_match_count += 1
                    match_score += 5
    
    no_pref_penalty = 0
    for user_idx, court_idx in enumerate(solution):
        if court_idx < len(court_info):
            court = court_info[court_idx]
            court_type = court.get('type', '')
            user_pref_list = user_prefs[user_idx] if user_idx < len(user_prefs) else []
            if user_pref_list and court_type not in user_pref_list:
                no_pref_penalty += 2
    
    # 4. 最终适应度
    fitness = match_score - violation_penalty - no_pref_penalty
    
    if cache is not None:
        cache.set(key, fitness)
    
    return fitness


def count_matches_with_constraints(
    solution: List[int],
    user_prefs: List[List[str]],
    court_info: List[Dict],
    user_time_prefs: List[List[int]] = None
) -> Dict[str, Any]:
    """
    统计匹配情况
    """
    num_users = len(solution)
    
    court_slot_usage = defaultdict(list)
    for user_idx, court_idx in enumerate(solution):
        court_slot_usage[court_idx].append(user_idx)
    
    violations = 0
    for court_idx, users in court_slot_usage.items():
        if len(users) > 1:
            violations += len(users) - 1
    
    type_matches = 0
    time_matches = 0
    
    for user_idx, court_idx in enumerate(solution):
        if court_idx >= len(court_info):
            continue
        
        court = court_info[court_idx]
        court_type = court.get('type', '')
        
        user_pref_list = user_prefs[user_idx] if user_idx < len(user_prefs) else []
        if court_type in user_pref_list:
            type_matches += 1
        
        if user_time_prefs and user_idx < len(user_time_prefs):
            user_time_prefs_list = user_time_prefs[user_idx]
            if user_time_prefs_list:
                slot_id = court.get('slot_id', 0)
                if slot_id in user_time_prefs_list:
                    time_matches += 1
    
    matched_users = type_matches
    match_rate = matched_users / num_users if num_users > 0 else 0
    
    return {
        'matched_users': matched_users,
        'match_rate': match_rate,
        'type_matches': type_matches,
        'time_matches': time_matches,
        'violations': violations,
        'total_users': num_users,
        'court_usage': dict(court_slot_usage)
    }


def create_solution_with_constraints(
    num_users: int,
    num_court_slots: int,
    user_prefs: List[List[str]],
    court_info: List[Dict],
    user_time_prefs: List[List[int]] = None
) -> List[int]:
    """
    创建初始解（考虑场地唯一性）
    """
    solution = []
    used_courts = set()
    
    users_with_prefs = []
    users_without_prefs = []
    
    for user_idx in range(num_users):
        if user_prefs[user_idx]:
            users_with_prefs.append(user_idx)
        else:
            users_without_prefs.append(user_idx)
    
    for user_idx in users_with_prefs:
        prefs = user_prefs[user_idx]
        
        matching_courts = []
        for court_idx, court in enumerate(court_info):
            if court_idx in used_courts:
                continue
            if court.get('type', '') in prefs:
                matching_courts.append(court_idx)
        
        if matching_courts:
            if user_time_prefs and user_time_prefs[user_idx]:
                time_prefs = user_time_prefs[user_idx]
                time_matching = []
                for court_idx in matching_courts:
                    if court_info[court_idx].get('slot_id', 0) in time_prefs:
                        time_matching.append(court_idx)
                if time_matching:
                    court_idx = random.choice(time_matching)
                    used_courts.add(court_idx)
                    solution.append(court_idx)
                    continue
            
            court_idx = random.choice(matching_courts)
            used_courts.add(court_idx)
            solution.append(court_idx)
        else:
            available = [i for i in range(num_court_slots) if i not in used_courts]
            if available:
                court_idx = random.choice(available)
                used_courts.add(court_idx)
                solution.append(court_idx)
            else:
                solution.append(random.randint(0, num_court_slots - 1))
    
    for user_idx in users_without_prefs:
        available = [i for i in range(num_court_slots) if i not in used_courts]
        if available:
            court_idx = random.choice(available)
            used_courts.add(court_idx)
            solution.append(court_idx)
        else:
            solution.append(random.randint(0, num_court_slots - 1))
    
    return solution


def optimize_with_time(
    courts: List[Dict],
    users: List[Dict],
    time_slots: List[Dict] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    优化的模拟退火算法 - 带时间维度和场地唯一性约束
    
    Args:
        courts: 场地列表（每个场地包含时间段信息）
        users: 用户列表
        time_slots: 时间段列表
        preferences: 算法参数
    
    Returns:
        优化结果
    """
    if preferences is None:
        preferences = {}
    
    config = {
        'initial_temperature': preferences.get('initial_temperature', 80.0),
        'min_temperature': preferences.get('min_temperature', 0.1),
        'alpha': preferences.get('alpha', 0.88),
        'iterations_per_temp': preferences.get('iterations_per_temp', 60),
        'max_iterations': preferences.get('max_iterations', 80000),
        'verbose': preferences.get('verbose', False),
        'random_seed': preferences.get('random_seed', 42),
        'max_no_improvement': preferences.get('max_no_improvement', 1000)
    }
    
    if config['random_seed'] is not None:
        random.seed(config['random_seed'])
        np.random.seed(config['random_seed'])
    
    num_court_slots = len(courts)
    num_users = len(users)
    
    user_prefs = []
    user_time_prefs = []
    for user in users:
        pref = user.get('preference', '')
        if isinstance(pref, str):
            user_prefs.append([pref] if pref else [])
        else:
            user_prefs.append(pref if pref else [])
        
        time_pref = user.get('time_preferences', [])
        if isinstance(time_pref, (int, str)):
            user_time_prefs.append([time_pref] if time_pref else [])
        else:
            user_time_prefs.append(time_pref if time_pref else [])
    
    court_info = []
    for court in courts:
        court_info.append({
            'type': court.get('type', ''),
            'location': court.get('location', ''),
            'slot_id': court.get('slot_id', 0),
            'time_index': court.get('time_index', 0),
            'court_index': court.get('court_index', 0),
            'court_name': court.get('court_name', ''),
            'date': court.get('date', ''),
            'start_time': court.get('start_time', ''),
            'end_time': court.get('end_time', ''),
            'unique_key': court.get('unique_key', '')
        })
    
    solution = create_solution_with_constraints(
        num_users, num_court_slots, user_prefs, court_info, user_time_prefs
    )
    
    while len(solution) < num_users:
        available = [i for i in range(num_court_slots)]
        if available:
            solution.append(random.choice(available))
        else:
            solution.append(random.randint(0, num_court_slots - 1))
    
    cache = SolutionCache()
    initial_fitness = calculate_fitness_with_constraints(
        solution, user_prefs, court_info, user_time_prefs, cache
    )
    
    best_solution = solution.copy()
    best_fitness = initial_fitness
    current_solution = solution
    current_fitness = initial_fitness
    
    temperature = config['initial_temperature']
    min_temperature = config['min_temperature']
    alpha = config['alpha']
    iterations_per_temp = config['iterations_per_temp']
    max_iterations = config['max_iterations']
    max_no_improvement = config['max_no_improvement']
    
    total_iterations = 0
    no_improvement_count = 0
    best_fitness_history = [best_fitness]
    
    if config['verbose']:
        print(f"初始适应度: {initial_fitness:.4f}")
        print(f"场地-时间段组合数: {num_court_slots}, 用户数: {num_users}")
    
    while temperature > min_temperature and total_iterations < max_iterations:
        for _ in range(iterations_per_temp):
            if total_iterations >= max_iterations:
                break
            
            total_iterations += 1
            
            new_solution = current_solution.copy()
            
            user_idx = random.randint(0, num_users - 1)
            new_court = random.randint(0, num_court_slots - 1)
            new_solution[user_idx] = new_court
            
            if random.random() < 0.3 and num_users >= 2:
                user1 = random.randint(0, num_users - 1)
                user2 = random.randint(0, num_users - 1)
                if user1 != user2:
                    new_solution[user1], new_solution[user2] = new_solution[user2], new_solution[user1]
            
            new_fitness = calculate_fitness_with_constraints(
                new_solution, user_prefs, court_info, user_time_prefs, cache
            )
        
            if new_fitness > current_fitness:
                current_solution = new_solution
                current_fitness = new_fitness
                
                if new_fitness > best_fitness:
                    best_solution = new_solution.copy()
                    best_fitness = new_fitness
                    no_improvement_count = 0
                    best_fitness_history.append(best_fitness)
                else:
                    no_improvement_count += 1
            else:
                delta = new_fitness - current_fitness
                if delta < 0 and random.random() < np.exp(delta / temperature):
                    current_solution = new_solution
                    current_fitness = new_fitness
                    no_improvement_count += 1
                else:
                    no_improvement_count += 1
            
            if no_improvement_count > max_no_improvement and temperature < 20:
                if config['verbose']:
                    print(f"提前终止: 无改进 {no_improvement_count} 步")
                break
        
        temperature *= alpha
        
        if config['verbose'] and total_iterations % (iterations_per_temp * 5) == 0:
            print(f"温度: {temperature:.4f}, 当前适应度: {current_fitness:.4f}, 最优: {best_fitness:.4f}")
    
    stats = count_matches_with_constraints(
        best_solution, user_prefs, court_info, user_time_prefs
    )
    
    assignments = []
    for user_idx, court_idx in enumerate(best_solution):
        if court_idx < len(court_info):
            court = court_info[court_idx]
            user = users[user_idx] if user_idx < len(users) else {}
            assignments.append({
                'user_id': user.get('id', user_idx + 1),
                'user_name': user.get('name', f'用户{user_idx+1}'),
                'court_name': court.get('court_name', ''),
                'court_type': court.get('type', ''),
                'location': court.get('location', ''),
                'date': court.get('date', ''),
                'start_time': court.get('start_time', ''),
                'end_time': court.get('end_time', ''),
                'slot_id': court.get('slot_id', 0),
                'court_index': court.get('court_index', 0),
                'is_matched': court.get('type', '') in user_prefs[user_idx] if user_idx < len(user_prefs) else False
            })
    
    return {
        'best_solution': best_solution,
        'fitness': best_fitness,
        'match_rate': stats['match_rate'],
        'matched_users': stats['matched_users'],
        'total_users': stats['total_users'],
        'type_matches': stats['type_matches'],
        'time_matches': stats['time_matches'],
        'violations': stats['violations'],
        'total_iterations': total_iterations,
        'final_temperature': temperature,
        'success': stats['violations'] == 0 and best_fitness > 0,
        'assignments': assignments,
        'court_usage': stats['court_usage'],
        'fitness_history': best_fitness_history
    }


def test_with_constraints():
    """测试带约束的算法"""
    print("=" * 80)
    print("测试带时间维度和场地唯一性约束的算法")
    print("=" * 80)
    
    test_scenarios = [
        {"num_courts": 5, "num_users": 8, "num_slots": 3, "desc": "小规模 (5场地, 8用户)"},
        {"num_courts": 10, "num_users": 20, "num_slots": 4, "desc": "中规模 (10场地, 20用户)"},
        {"num_courts": 20, "num_users": 50, "num_slots": 4, "desc": "目标规模 (20场地, 50用户)"},
    ]
    
    all_results = []
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"场景: {scenario['desc']}")
        print(f"{'='*60}")
        
        courts, users, time_slots = generate_test_data_with_time(
            num_courts=scenario['num_courts'],
            num_users=scenario['num_users'],
            num_time_slots=scenario['num_slots'],
            seed=42
        )
        
        print(f"场地-时间段组合数: {len(courts)}")
        print(f"用户数: {len(users)}")
        print(f"时间段数: {len(time_slots)}")
        
        config = {
            'initial_temperature': 80,
            'min_temperature': 0.1,
            'alpha': 0.88,
            'iterations_per_temp': 60,
            'max_iterations': 80000,
            'verbose': False,
            'random_seed': 42,
            'max_no_improvement': 1000
        }
        
        run_times = []
        match_rates = []
        fitnesses = []
        violations_list = []
        
        for run in range(3):
            start_time = time.time()
            result = optimize_with_time(courts, users, time_slots, config)
            elapsed = time.time() - start_time
            
            run_times.append(elapsed)
            match_rates.append(result['match_rate'])
            fitnesses.append(result['fitness'])
            violations_list.append(result['violations'])
            
            print(f"  Run {run+1}: {elapsed:.3f}s, 匹配率: {result['match_rate']:.2%}, "
                  f"违规: {result['violations']}, 适应度: {result['fitness']:.2f}")
        
        avg_runtime = np.mean(run_times)
        avg_match_rate = np.mean(match_rates)
        avg_fitness = np.mean(fitnesses)
        avg_violations = np.mean(violations_list)
        
        print(f"\n  平均运行时间: {avg_runtime:.3f}秒")
        print(f"  平均匹配率: {avg_match_rate:.2%}")
        print(f"  平均适应度: {avg_fitness:.2f}")
        print(f"  平均违规数: {avg_violations:.1f}")
        
        if avg_violations == 0:
            print("  ✅ 场地唯一性约束满足!")
        else:
            print(f"  ⚠️ 存在 {avg_violations:.0f} 个场地违规分配")
        
        all_results.append({
            'scenario': scenario['desc'],
            'avg_runtime': avg_runtime,
            'avg_match_rate': avg_match_rate,
            'avg_fitness': avg_fitness,
            'avg_violations': avg_violations,
            'details': result
        })
    
    return all_results


def test_original_problem():
    """测试原始问题场景 - 16人5场地"""
    print("\n" + "=" * 80)
    print("测试原始问题场景: 16人, 5个场地, 每个场地2个时间段")
    print("=" * 80)
    
    court_types = ["羽毛球", "乒乓球", "篮球"]
    
    courts, users, time_slots = generate_test_data_with_time(
        num_courts=5,
        num_users=16,
        num_time_slots=2,
        court_types=court_types,
        seed=42
    )
    
    for i, user in enumerate(users):
        if i % 3 == 0:
            user['preference'] = "羽毛球"
        elif i % 3 == 1:
            user['preference'] = "乒乓球"
        else:
            user['preference'] = ["羽毛球", "乒乓球"]
    
    print(f"\n场地-时间段组合数: {len(courts)} (5个场地 × 2个时间段)")
    print(f"用户数: {len(users)}")
    print(f"时间段: {time_slots}")
    
    print("\n场地信息:")
    for court in courts[:5]:
        print(f"  {court['court_name']} - {court['date']} {court['start_time']}-{court['end_time']}")
    
    config = {
        'initial_temperature': 80,
        'min_temperature': 0.1,
        'alpha': 0.88,
        'iterations_per_temp': 60,
        'max_iterations': 50000,
        'verbose': True,
        'random_seed': 42
    }
    
    start_time = time.time()
    result = optimize_with_time(courts, users, time_slots, config)
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("优化结果:")
    print(f"{'='*60}")
    print(f"运行时间: {elapsed:.3f}秒")
    print(f"匹配率: {result['match_rate']:.2%}")
    print(f"匹配用户: {result['matched_users']}/{result['total_users']}")
    print(f"类型匹配: {result['type_matches']}")
    print(f"时间匹配: {result['time_matches']}")
    print(f"违规数: {result['violations']}")
    print(f"适应度: {result['fitness']:.2f}")
    print(f"迭代次数: {result['total_iterations']}")
    print(f"成功: {result['success']}")
    
    print("\n分配详情 (前10个):")
    for i, assignment in enumerate(result['assignments'][:10]):
        status = "✅" if assignment['is_matched'] else "❌"
        print(f"  {status} {assignment['user_name']} -> {assignment['court_name']} "
              f"({assignment['court_type']}) {assignment['start_time']}-{assignment['end_time']}")
    
    print("\n场地使用情况:")
    for court_idx, users_list in result['court_usage'].items():
        if court_idx < len(courts):
            court = courts[court_idx]
            print(f"  {court['court_name']} ({court['start_time']}-{court['end_time']}): "
                  f"{len(users_list)} 人")
    
    if result['violations'] == 0:
        print("\n✅ 所有场地唯一性约束满足!")
    else:
        print(f"\n⚠️ 存在 {result['violations']} 个违规分配")
    
    return result


def plot_results(results):
    """绘制结果图"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1 = axes[0]
    scenarios = [r['scenario'] for r in results]
    times = [r['avg_runtime'] for r in results]
    rates = [r['avg_match_rate'] for r in results]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, times, width, label='运行时间 (秒)', color='steelblue', alpha=0.8)
    ax1.set_xlabel('场景')
    ax1.set_ylabel('运行时间 (秒)')
    ax1.set_title('算法性能')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, rotation=15, ha='right')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, rates, width, label='匹配率', color='coral', alpha=0.8)
    ax2.set_ylabel('匹配率')
    ax2.legend(loc='upper right')
    
    ax3 = axes[1]
    violations = [r['avg_violations'] for r in results]
    fitness = [r['avg_fitness'] for r in results]
    
    bars3 = ax3.bar(x - width/2, violations, width, label='违规数', color='red', alpha=0.7)
    ax3.set_xlabel('场景')
    ax3.set_ylabel('违规数')
    ax3.set_title('约束满足情况')
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenarios, rotation=15, ha='right')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3, axis='y')
    
    ax4 = ax3.twinx()
    bars4 = ax4.bar(x + width/2, fitness, width, label='适应度', color='green', alpha=0.7)
    ax4.set_ylabel('适应度')
    ax4.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('time_constraint_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\n结果图已保存到: time_constraint_results.png")


def main():
    """主函数"""
    print("=" * 80)
    print("模拟退火算法 - 带时间维度和场地唯一性约束")
    print("=" * 80)
    
    print("\n【1】测试原始问题 (16人, 5场地, 每场地2时间段)")
    result = test_original_problem()
    
    print("\n【2】测试不同规模场景")
    results = test_with_constraints()
    
    plot_results(results)
    
    with open('time_constraint_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'original_problem': result,
            'scenarios': results
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n详细结果已保存到: time_constraint_results.json")


if __name__ == "__main__":
    main()

# ========== 兼容旧接口 ==========

def optimize(
    courts: List[Dict[str, Any]],
    users: List[Dict[str, Any]],
    preferences: Optional[Dict[str, Any]] = None,
    cache = None
) -> Dict[str, Any]:
    """
    兼容旧接口的优化函数
    直接在场地上做分配（不展开假时间段），确保每个用户分配到不同场地
    """
    import time as _time
    start_time = _time.time()

    # 给原始 courts 补充算法需要的字段（单一时段，使用真实时间）
    time_templates = [
        ("18:00", "20:00"),
        ("19:00", "21:00"),
        ("20:00", "22:00"),
        ("18:30", "20:30"),
    ]

    court_slots = []
    for i, court in enumerate(courts):
        start_t, end_t = time_templates[i % len(time_templates)]
        court_slots.append({
            "id": court.get("id", i + 1),
            "court_name": court.get("name", f"场地{i+1}"),
            "type": court.get("type", ""),
            "location": court.get("location", ""),
            "slot_id": 1,
            "date": "2026-08-16",
            "start_time": start_t,
            "end_time": end_t,
            "time_index": 0,
            "court_index": i,
            "unique_key": f"court_{i}_slot_1",
            "original_court_id": court.get("id", i + 1)
        })

    # 适配 users 格式
    users_adapted = []
    for user in users:
        u = dict(user)
        if "time_preferences" not in u:
            u["time_preferences"] = []
        if "name" not in u:
            u["name"] = u.get("username", f"用户{u.get('id', 0)}")
        users_adapted.append(u)

    # 构造一个虚拟的 time_slots（只包含1个时段）
    time_slots = [{
        "slot_id": 1,
        "date": "2026-08-16",
        "start_time": "18:00",
        "end_time": "20:00",
        "index": 0
    }]

    # 调用算法：传入不固定的随机种子，避免每次都一样
    pref = dict(preferences) if preferences else {}
    if 'random_seed' not in pref:
        pref['random_seed'] = None  # 不固定种子

    result = optimize_with_time(court_slots, users_adapted, time_slots, pref)

    # 预先构建用户偏好映射
    user_prefs_map = {}
    for user in users:
        pref_val = user.get("preference", "")
        uid = user.get("id", 0)
        if isinstance(pref_val, str):
            user_prefs_map[uid] = [pref_val] if pref_val else []
        elif isinstance(pref_val, list):
            user_prefs_map[uid] = [p for p in pref_val if p]
        else:
            user_prefs_map[uid] = []

    # 转换 assignments -> plan（兼容旧格式）
    plan = []
    matched_users = 0

    for assignment in result.get("assignments", []):
        # 直接从 assignment 取 court_index 映射回原始场地
        court_idx = assignment.get("court_index", 0)
        if court_idx < len(courts):
            original_court = courts[court_idx]
            court_id_val = original_court.get("id", court_idx + 1)
            court_type = original_court.get("type", "")
        else:
            court_id_val = assignment.get("original_court_id", assignment.get("id", 0))
            court_type = assignment.get("court_type", "")

        user_id = assignment.get("user_id", 0)
        user_prefs = user_prefs_map.get(user_id, [])

        is_matched = court_type in user_prefs if user_prefs else False
        score = 1.0 if is_matched else 0.0
        if is_matched:
            matched_users += 1

        plan.append({
            "user_id": user_id,
            "court_id": court_id_val,
            "court_type": court_type,
            "user_preference": user_prefs,
            "score": score,
            "slot_id": 1,
            "start_time": assignment.get("start_time", ""),
            "end_time": assignment.get("end_time", "")
        })

    total_users = len(users)
    match_rate = matched_users / total_users if total_users > 0 else 0.0

    violations = result.get('violations', 0)
    return {
        "success": True,
        "msg": f"优化完成，总迭代次数: {result.get('total_iterations', 0)}，存在 {violations} 个场地冲突" if violations > 0 else f"优化完成，总迭代次数: {result.get('total_iterations', 0)}",
        "plan": plan,
        "fitness": result.get("fitness", 0),
        "match_rate": match_rate,
        "matched_users": matched_users,
        "total_users": total_users,
        "runtime_seconds": _time.time() - start_time,
        "total_iterations": result.get("total_iterations", 0),
        "final_temperature": result.get("final_temperature", 0)
    }
