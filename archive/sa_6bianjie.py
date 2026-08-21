"""
边界测试 - 模拟退火算法
测试各种极端输入情况
"""

import sys
import traceback
from sa_youhua import optimize, SolutionCache, init_solution, calculate_fitness_fast

def run_test(test_name, courts, users, preferences=None):
    """运行单个测试用例"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"{'='*60}")
    print(f"场地数: {len(courts)}, 用户数: {len(users)}")
    
    try:
        result = optimize(courts, users, preferences=preferences)
        
        print(f"✅ 成功: {result['success']}")
        print(f"信息: {result['msg']}")
        print(f"匹配率: {result['match_rate']:.2%}")
        print(f"匹配用户数: {result['matched_users']}/{result['total_users']}")
        print(f"适应度: {result['fitness']}")
        print(f"运行时间: {result['runtime_seconds']:.4f}秒")
        
        if result['plan']:
            print(f"计划分配数: {len(result['plan'])}")
            # 显示前3个分配
            for i, item in enumerate(result['plan'][:3]):
                print(f"  分配{i+1}: 用户{item['user_id']} -> 场地{item['court_id']}, 得分={item['score']}")
            if len(result['plan']) > 3:
                print(f"  ... (共{len(result['plan'])}个分配)")
        
        return True, result
    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False, None

def test_empty_courts():
    """测试：场地数为0"""
    courts = []
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 2, "preference": "乒乓球"},
        {"id": 3, "preference": "篮球"}
    ]
    return run_test("场地数为0", courts, users)

def test_empty_users():
    """测试：用户数为0"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"}
    ]
    users = []
    return run_test("用户数为0", courts, users)

def test_empty_both():
    """测试：场地和用户都为0"""
    courts = []
    users = []
    return run_test("场地和用户都为0", courts, users)

def test_all_same_preference():
    """测试：所有人偏好同一种场地"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "羽毛球", "location": "B区"},
        {"id": 3, "type": "羽毛球", "location": "C区"},
        {"id": 4, "type": "乒乓球", "location": "D区"},
        {"id": 5, "type": "乒乓球", "location": "E区"}
    ]
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 2, "preference": "羽毛球"},
        {"id": 3, "preference": "羽毛球"},
        {"id": 4, "preference": "羽毛球"},
        {"id": 5, "preference": "羽毛球"},
        {"id": 6, "preference": "羽毛球"},
        {"id": 7, "preference": "羽毛球"}
    ]
    return run_test("所有人偏好同一种场地（羽毛球）", courts, users)

def test_no_preferences():
    """测试：用户没有偏好"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"},
        {"id": 3, "type": "篮球", "location": "C区"}
    ]
    users = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5}
    ]
    return run_test("用户无偏好", courts, users)

def test_more_users_than_courts():
    """测试：用户数远多于场地数"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"},
        {"id": 3, "type": "篮球", "location": "C区"}
    ]
    users = [
        {"id": i, "preference": ["羽毛球", "乒乓球", "篮球"][i % 3]}
        for i in range(1, 51)
    ]
    return run_test("50个用户 vs 3个场地", courts, users)

def test_more_courts_than_users():
    """测试：场地数远多于用户数"""
    courts = [
        {"id": i, "type": ["羽毛球", "乒乓球", "篮球", "网球", "足球"][i % 5], 
         "location": f"区域{i%3+1}"}
        for i in range(1, 101)
    ]
    users = [
        {"id": i, "preference": ["羽毛球", "乒乓球", "篮球"][i % 3]}
        for i in range(1, 6)
    ]
    return run_test("100个场地 vs 5个用户", courts, users)

def test_one_user_one_court():
    """测试：1个用户，1个场地"""
    courts = [{"id": 1, "type": "羽毛球", "location": "A区"}]
    users = [{"id": 1, "preference": "羽毛球"}]
    return run_test("1个用户，1个场地（匹配）", courts, users)

def test_one_user_one_court_no_match():
    """测试：1个用户，1个场地（不匹配）"""
    courts = [{"id": 1, "type": "羽毛球", "location": "A区"}]
    users = [{"id": 1, "preference": "乒乓球"}]
    return run_test("1个用户，1个场地（不匹配）", courts, users)

def test_all_courts_same_type():
    """测试：所有场地类型相同"""
    courts = [
        {"id": 1, "type": "通用", "location": "A区"},
        {"id": 2, "type": "通用", "location": "B区"},
        {"id": 3, "type": "通用", "location": "C区"},
        {"id": 4, "type": "通用", "location": "D区"},
        {"id": 5, "type": "通用", "location": "E区"}
    ]
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 2, "preference": "乒乓球"},
        {"id": 3, "preference": "篮球"},
        {"id": 4, "preference": "羽毛球"},
        {"id": 5, "preference": "乒乓球"}
    ]
    return run_test("所有场地类型相同", courts, users)

def test_missing_fields():
    """测试：缺失字段"""
    courts = [
        {"id": 1},
        {"id": 2, "type": "乒乓球", "location": "B区"}
    ]
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 2}
    ]
    return run_test("缺失字段", courts, users)

def test_duplicate_ids():
    """测试：重复ID"""
    courts = [
        {"id": 1, "type": "羽毛球"},
        {"id": 1, "type": "乒乓球"},
        {"id": 2, "type": "篮球"}
    ]
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 1, "preference": "乒乓球"},
        {"id": 2, "preference": "篮球"}
    ]
    return run_test("重复ID", courts, users)

def test_invalid_data_types():
    """测试：无效数据类型"""
    courts = [
        {"id": "1", "type": "羽毛球"},
        {"id": 2, "type": 123},
        {"id": 3, "type": None}
    ]
    users = [
        {"id": "1", "preference": "羽毛球"},
        {"id": 2, "preference": None},
        {"id": 3}
    ]
    return run_test("无效数据类型", courts, users)

def test_large_scale():
    """测试：大规模数据（100个场地，100个用户）"""
    courts = [
        {"id": i, "type": ["羽毛球", "乒乓球", "篮球", "网球", "足球", "排球", "游泳", "健身"][i % 8],
         "location": f"区域{i%5+1}"}
        for i in range(1, 101)
    ]
    users = [
        {"id": i, "preference": ["羽毛球", "乒乓球", "篮球", "网球", "足球", "排球"][i % 6]}
        for i in range(1, 101)
    ]
    return run_test("大规模数据：100个场地，100个用户", courts, users)

def test_extreme_preferences():
    """测试：极端偏好（空字符串、特殊字符）"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"},
        {"id": 3, "type": "羽毛球", "location": "C区"}
    ]
    users = [
        {"id": 1, "preference": ""},
        {"id": 2, "preference": " "},
        {"id": 3, "preference": "\t"},
        {"id": 4, "preference": "羽毛球"},
        {"id": 5, "preference": "特别特别长的偏好字符串" * 10}
    ]
    return run_test("极端偏好值", courts, users)

def test_no_users_but_courts_exist():
    """测试：有场地但无用户"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"},
        {"id": 3, "type": "篮球", "location": "C区"}
    ]
    users = []
    return run_test("有场地但无用户", courts, users)

def test_no_courts_but_users_exist():
    """测试：有用户但无场地"""
    courts = []
    users = [
        {"id": 1, "preference": "羽毛球"},
        {"id": 2, "preference": "乒乓球"},
        {"id": 3, "preference": "篮球"}
    ]
    return run_test("有用户但无场地", courts, users)

def test_boundary_iterations():
    """测试：极少的迭代次数"""
    courts = [
        {"id": 1, "type": "羽毛球", "location": "A区"},
        {"id": 2, "type": "乒乓球", "location": "B区"},
        {"id": 3, "type": "篮球", "location": "C区"}
    ]
    users = [
        {"id": i, "preference": ["羽毛球", "乒乓球", "篮球"][i % 3]}
        for i in range(1, 11)
    ]
    preferences = {
        "initial_temperature": 1.0,
        "min_temperature": 0.9,
        "max_iterations": 10,
        "iterations_per_temp": 2,
        "alpha": 0.9,
        "verbose": False
    }
    return run_test("极少迭代次数（10次）", courts, users, preferences)

def main():
    """运行所有边界测试"""
    print("="*60)
    print("模拟退火算法 - 边界测试")
    print("="*60)
    
    test_cases = [
        ("空场地", test_empty_courts),
        ("空用户", test_empty_users),
        ("都为空", test_empty_both),
        ("所有人偏好同一种场地", test_all_same_preference),
        ("用户无偏好", test_no_preferences),
        ("50用户3场地", test_more_users_than_courts),
        ("100场地5用户", test_more_courts_than_users),
        ("1用户1场地匹配", test_one_user_one_court),
        ("1用户1场地不匹配", test_one_user_one_court_no_match),
        ("所有场地类型相同", test_all_courts_same_type),
        ("缺失字段", test_missing_fields),
        ("重复ID", test_duplicate_ids),
        ("无效数据类型", test_invalid_data_types),
        ("大规模数据", test_large_scale),
        ("极端偏好值", test_extreme_preferences),
        ("有场地无用户", test_no_users_but_courts_exist),
        ("有用户无场地", test_no_courts_but_users_exist),
        ("极少迭代", test_boundary_iterations)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in test_cases:
        success, _ = test_func()
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有边界测试通过！算法在极端输入下表现稳健。")
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，需要检查。")
    
    print("="*60)

if __name__ == "__main__":
    main()