# 启动Flask并完整测试所有API
import subprocess
import time
import requests
import json

proc = subprocess.Popen(
    [r'C:\Users\five_\miniconda3\envs\flask-env\python.exe', r'C:\Users\five_\PycharmProjects\FlaskProject\app.py'],
    cwd=r'C:\Users\five_\PycharmProjects\FlaskProject',
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True
)

time.sleep(3)

try:
    # 1. 测试注册管理员
    print('=== 1. 注册管理员 ===')
    r = requests.post('http://127.0.0.1:5000/api/register', 
        json={'username': 'admin_test', 'password': '123456', 'invite_code': 'admin666'}, timeout=5)
    print(r.json())

    # 2. 登录管理员
    print('\n=== 2. 登录管理员 ===')
    r = requests.post('http://127.0.0.1:5000/api/login', 
        json={'username': 'admin_test', 'password': '123456'}, timeout=5)
    print(r.json())
    token = r.json().get('data', {}).get('token', '')

    # 3. 获取用户列表
    print('\n=== 3. /api/users ===')
    r = requests.get('http://127.0.0.1:5000/api/users', headers={'Authorization': token}, timeout=5)
    data = r.json()
    users = data.get('data', [])
    print(f'用户数量: {len(users)}')
    for u in users[:5]:
        print(f'  {u}')
    if len(users) > 5:
        print(f'  ... 共 {len(users)} 个')

    # 4. 获取场地
    print('\n=== 4. /api/courts ===')
    r = requests.get('http://127.0.0.1:5000/api/courts', timeout=5)
    courts = r.json().get('data', [])
    print(f'场地数量: {len(courts)}')

    # 5. 执行优化
    print('\n=== 5. /api/optimize ===')
    r = requests.post('http://127.0.0.1:5000/api/optimize',
        json={'courts': courts, 'users': users},
        headers={'Authorization': token}, timeout=10)
    opt = r.json()
    print(json.dumps(opt, indent=2, ensure_ascii=False))

    # 6. 普通用户访问优化（应该403）
    print('\n=== 6. 普通用户访问优化（应403）===')
    r2 = requests.post('http://127.0.0.1:5000/api/login',
        json={'username': 'user', 'password': '123456'}, timeout=5)
    user_token = r2.json().get('data', {}).get('token', '')
    r3 = requests.post('http://127.0.0.1:5000/api/optimize',
        json={'courts': courts, 'users': users},
        headers={'Authorization': user_token}, timeout=5)
    print(r3.json())

except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
    print('\n=== 测试完成 ===')
