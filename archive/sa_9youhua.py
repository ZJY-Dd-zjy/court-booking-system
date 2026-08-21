"""
模拟退火算法性能优化
====================
针对20场地50用户场景进行性能优化
"""

import random
import time
import json
import sys
import os
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt

from sa_7tiaozheng import optimize, SolutionCache, calculate_fitness_fast

def generate_test_data(
    num_courts: int, 
    num_users: int,
    court_types: List[str] = None,
    seed: int = 42
) -> Tuple[List[Dict], List[Dict]]:
    """生成测试数据"""
    random.seed(seed)
    
    if court_types is None:
        court_types = ["羽毛球", "乒乓球", "篮球", "足球", "网球", "排球", "游泳", "健身"]
    
    courts = []
    for i in range(num_courts):
        court_type = random.choice(court_types)
        courts.append({
            "id": i + 1,
            "type": court_type,
            "location": f"{chr(65 + i % 5)}区"
        })
    
    users = []
    for i in range(num_users):
        num_prefs = random.choices([0, 1, 2], weights=[0.2, 0.5, 0.3])[0]
        if num_prefs > 0:
            prefs = random.sample(court_types, min(num_prefs, len(court_types)))
        else:
            prefs = []
        
        users.append({
            "id": i + 1,
            "preference": prefs if len(prefs) > 1 else (prefs[0] if prefs else "")
        })
    
    return courts, users

def test_original_performance():
    """测试原始算法的性能"""
    print("=" * 60)
    print("测试原始算法性能 (20场地, 50用户)")
    print("=" * 60)
    
    courts, users = generate_test_data(20, 50, seed=42)
    
    test_configs = [
        {"name": "默认配置", "params": {
            'initial_temperature': 100,
            'min_temperature': 0.01,
            'alpha': 0.95,
            'iterations_per_temp': 100,
            'max_iterations': 100000,
            'verbose': False
        }},
        {"name": "快速配置1", "params": {
            'initial_temperature': 50,
            'min_temperature': 0.1,
            'alpha': 0.85,
            'iterations_per_temp': 50,
            'max_iterations': 50000,
            'verbose': False
        }},
        {"name": "快速配置2", "params": {
            'initial_temperature': 30,
            'min_temperature': 0.1,
            'alpha': 0.80,
            'iterations_per_temp': 30,
            'max_iterations': 30000,
            'verbose': False
        }},
    ]
    
    results = []
    for config in test_configs:
        print(f"\n测试: {config['name']}")
        print(f"参数: {config['params']}")
        
        start_time = time.time()
        result = optimize(courts, users, preferences=config['params'])
        elapsed = time.time() - start_time
        
        fitness = result.get('fitness', 0)
        match_rate = result.get('match_rate', 0)
        matched_users = result.get('matched_users', 0)
        total_users = result.get('total_users', 0)
        iterations = result.get('total_iterations', 0)
        
        print(f"  运行时间: {elapsed:.3f}秒")
        print(f"  匹配率: {match_rate:.2%}")
        print(f"  适应度: {fitness:.4f}")
        print(f"  匹配用户: {matched_users}/{total_users}")
        print(f"  迭代次数: {iterations}")
        
        results.append({
            'name': config['name'],
            'params': config['params'],
            'runtime': elapsed,
            'match_rate': match_rate,
            'fitness': fitness,
            'matched_users': matched_users,
            'total_users': total_users,
            'iterations': iterations
        })
    
    return results

def create_optimized_algorithm():
    """创建优化版本的算法"""
    
    def optimize_fast(
        courts: List[Dict],
        users: List[Dict],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        优化版本的模拟退火算法
        针对20场地50用户场景优化
        """
        if preferences is None:
            preferences = {}
        
        config = {
            'initial_temperature': preferences.get('initial_temperature', 50.0),
            'min_temperature': preferences.get('min_temperature', 0.1),
            'alpha': preferences.get('alpha', 0.85),
            'iterations_per_temp': preferences.get('iterations_per_temp', 50),
            'max_iterations': preferences.get('max_iterations', 50000),
            'verbose': preferences.get('verbose', False),
            'random_seed': preferences.get('random_seed', 42)
        }
        
        if config['random_seed'] is not None:
            random.seed(config['random_seed'])
            np.random.seed(config['random_seed'])
        
        num_courts = len(courts)
        num_users = len(users)
        
        user_prefs = []
        for user in users:
            pref = user.get('preference', '')
            if isinstance(pref, str):
                user_prefs.append([pref] if pref else [])
            else:
                user_prefs.append(pref if pref else [])
        
        court_type_indices = []
        court_locations = []
        for court in courts:
            court_type = court.get('type', '')
            court_type_indices.append(court_type)
            court_locations.append(court.get('location', ''))
        
        solution = []
        for user_idx in range(num_users):
            prefs = user_prefs[user_idx]
            if prefs:
                matched_courts = [i for i, ct in enumerate(court_type_indices) if ct in prefs]
                if matched_courts:
                    court_idx = random.choice(matched_courts)
                else:
                    court_idx = random.randint(0, num_courts - 1)
            else:
                court_idx = random.randint(0, num_courts - 1)
            solution.append(court_idx)
        
        cache = SolutionCache()
        initial_fitness = calculate_fitness_fast(solution, user_prefs, court_type_indices, cache)
        best_solution = solution.copy()
        best_fitness = initial_fitness
        
        if config['verbose']:
            print(f"初始适应度: {initial_fitness:.4f}")
        
        temperature = config['initial_temperature']
        min_temperature = config['min_temperature']
        alpha = config['alpha']
        iterations_per_temp = config['iterations_per_temp']
        max_iterations = config['max_iterations']
        
        current_solution = solution
        current_fitness = initial_fitness
        total_iterations = 0
        no_improvement_count = 0
        max_no_improvement = 500
        
        def count_matches(sol):
            matches = 0
            for user_idx, court_idx in enumerate(sol):
                if court_type_indices[court_idx] in user_prefs[user_idx]:
                    matches += 1
            return matches
        
        best_matches = count_matches(best_solution)
        
        while temperature > min_temperature and total_iterations < max_iterations:
            for _ in range(iterations_per_temp):
                if total_iterations >= max_iterations:
                    break
                
                total_iterations += 1
                
                new_solution = current_solution.copy()
                user_idx = random.randint(0, num_users - 1)
                new_court = random.randint(0, num_courts - 1)
                new_solution[user_idx] = new_court
                
                new_fitness = calculate_fitness_fast(new_solution, user_prefs, court_type_indices, cache)
                
                if new_fitness > current_fitness:
                    current_solution = new_solution
                    current_fitness = new_fitness
                    
                    if new_fitness > best_fitness:
                        best_solution = new_solution.copy()
                        best_fitness = new_fitness
                        best_matches = count_matches(best_solution)
                        no_improvement_count = 0
                    else:
                        no_improvement_count += 1
                else:
                    delta = new_fitness - current_fitness
                    if random.random() < np.exp(delta / temperature):
                        current_solution = new_solution
                        current_fitness = new_fitness
                        no_improvement_count += 1
                    else:
                        no_improvement_count += 1
                
                if no_improvement_count > max_no_improvement and temperature < 10:
                    if config['verbose']:
                        print(f"提前终止: 无改进 {no_improvement_count} 步")
                    break
            
            temperature *= alpha
            
            if config['verbose'] and total_iterations % (iterations_per_temp * 10) == 0:
                print(f"温度: {temperature:.4f}, 当前适应度: {current_fitness:.4f}, 最优: {best_fitness:.4f}")
        
        total_users = num_users
        matched_users = best_matches
        
        match_rate = matched_users / total_users if total_users > 0 else 0
        
        return {
            'best_solution': best_solution,
            'fitness': best_fitness,
            'match_rate': match_rate,
            'matched_users': matched_users,
            'total_users': total_users,
            'total_iterations': total_iterations,
            'success': best_fitness > 0,
            'final_temperature': temperature
        }
    
    return optimize_fast

def test_optimized_performance():
    """测试优化算法的性能"""
    print("\n" + "=" * 60)
    print("测试优化算法性能 (20场地, 50用户)")
    print("=" * 60)
    
    courts, users = generate_test_data(20, 50, seed=42)
    optimize_fast = create_optimized_algorithm()
    
    test_configs = [
        {"name": "优化配置1", "params": {
            'initial_temperature': 50,
            'min_temperature': 0.1,
            'alpha': 0.85,
            'iterations_per_temp': 50,
            'max_iterations': 50000,
            'verbose': False
        }},
        {"name": "优化配置2", "params": {
            'initial_temperature': 30,
            'min_temperature': 0.1,
            'alpha': 0.80,
            'iterations_per_temp': 30,
            'max_iterations': 30000,
            'verbose': False
        }},
        {"name": "优化配置3", "params": {
            'initial_temperature': 20,
            'min_temperature': 0.05,
            'alpha': 0.75,
            'iterations_per_temp': 20,
            'max_iterations': 20000,
            'verbose': False
        }},
    ]
    
    results = []
    for config in test_configs:
        print(f"\n测试: {config['name']}")
        print(f"参数: {config['params']}")
        
        run_times = []
        match_rates = []
        fitnesses = []
        
        for run in range(3):
            start_time = time.time()
            result = optimize_fast(courts, users, preferences=config['params'])
            elapsed = time.time() - start_time
            
            run_times.append(elapsed)
            match_rates.append(result['match_rate'])
            fitnesses.append(result['fitness'])
        
        avg_runtime = np.mean(run_times)
        avg_match_rate = np.mean(match_rates)
        avg_fitness = np.mean(fitnesses)
        std_runtime = np.std(run_times)
        
        print(f"  平均运行时间: {avg_runtime:.3f}秒 (±{std_runtime:.3f})")
        print(f"  平均匹配率: {avg_match_rate:.2%}")
        print(f"  平均适应度: {avg_fitness:.4f}")
        
        results.append({
            'name': config['name'],
            'params': config['params'],
            'avg_runtime': avg_runtime,
            'std_runtime': std_runtime,
            'avg_match_rate': avg_match_rate,
            'avg_fitness': avg_fitness,
            'run_times': run_times,
            'match_rates': match_rates
        })
    
    return results

def performance_comparison():
    """性能对比分析"""
    print("\n" + "=" * 60)
    print("性能对比分析")
    print("=" * 60)
    
    original_results = test_original_performance()
    
    optimized_results = test_optimized_performance()
    
    print("\n" + "=" * 60)
    print("对比分析总结")
    print("=" * 60)
    
    print("\n原始算法最佳配置:")
    best_orig = min(original_results, key=lambda x: x['runtime'])
    print(f"  配置: {best_orig['name']}")
    print(f"  运行时间: {best_orig['runtime']:.3f}秒")
    print(f"  匹配率: {best_orig['match_rate']:.2%}")
    print(f"  适应度: {best_orig['fitness']:.4f}")
    
    print("\n优化算法最佳配置:")
    best_opt = min(optimized_results, key=lambda x: x['avg_runtime'])
    print(f"  配置: {best_opt['name']}")
    print(f"  运行时间: {best_opt['avg_runtime']:.3f}秒 (±{best_opt['std_runtime']:.3f})")
    print(f"  匹配率: {best_opt['avg_match_rate']:.2%}")
    print(f"  适应度: {best_opt['avg_fitness']:.4f}")
    
    print("\n性能提升:")
    speedup = best_orig['runtime'] / best_opt['avg_runtime']
    print(f"  速度提升: {speedup:.2f}x")
    print(f"  时间减少: {(1 - best_opt['avg_runtime']/best_orig['runtime'])*100:.1f}%")
    print(f"  匹配率变化: {best_opt['avg_match_rate'] - best_orig['match_rate']:+.2%}")
    
    if best_opt['avg_runtime'] < 3.0:
        print("\n✅ 达标! 运行时间小于3秒")
    else:
        print(f"\n⚠️ 运行时间 {best_opt['avg_runtime']:.3f}秒，需要进一步优化")
    
    return original_results, optimized_results, best_opt

def plot_performance_comparison(original_results, optimized_results):
    """绘制性能对比图"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1 = axes[0]
    names = [r['name'] for r in original_results] + [r['name'] for r in optimized_results]
    times = [r['runtime'] for r in original_results] + [r['avg_runtime'] for r in optimized_results]
    colors = ['blue'] * len(original_results) + ['green'] * len(optimized_results)
    
    bars = ax1.bar(names, times, color=colors, alpha=0.7)
    ax1.axhline(y=3.0, color='red', linestyle='--', label='目标 (3秒)')
    ax1.set_ylabel('运行时间 (秒)')
    ax1.set_title('算法性能对比')
    ax1.set_xticklabels(names, rotation=15, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = axes[1]
    rates = [r['match_rate'] for r in original_results] + [r['avg_match_rate'] for r in optimized_results]
    bars = ax2.bar(names, rates, color=colors, alpha=0.7)
    ax2.set_ylabel('匹配率')
    ax2.set_title('匹配率对比')
    ax2.set_xticklabels(names, rotation=15, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\n性能对比图已保存到: performance_comparison.png")

def main():
    """主函数"""
    print("=" * 80)
    print("模拟退火算法性能优化")
    print("目标: 20场地50用户场景下运行时间 < 3秒")
    print("=" * 80)
    
    original_results, optimized_results, best_config = performance_comparison()
    
    plot_performance_comparison(original_results, optimized_results)
    
    print("\n" + "=" * 80)
    print("【最终建议】")
    print("=" * 80)
    print("\n推荐使用以下优化配置:")
    print("-" * 40)
    for key, value in best_config['params'].items():
        print(f"    {key} = {value}")
    
    print(f"\n预计运行时间: {best_config['avg_runtime']:.3f}秒 (±{best_config['std_runtime']:.3f})")
    print(f"预计匹配率: {best_config['avg_match_rate']:.2%}")
    
    with open("optimization_results.json", "w", encoding="utf-8") as f:
        json.dump({
            'best_config': best_config,
            'original_results': original_results,
            'optimized_results': optimized_results
        }, f, indent=2, ensure_ascii=False)
    
    print("\n详细结果已保存到: optimization_results.json")

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
