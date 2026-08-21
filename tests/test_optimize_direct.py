# 直接测试 /api/optimize
import requests

# 先登录获取管理员 token
login_resp = requests.post('http://127.0.0.1:5000/api/login', json={
    'username': 'admin',
    'password': 'admin123'
})
print('登录结果:', login_resp.json())

token = login_resp.json().get('data', {}).get('token', '')
if not token:
    print('登录失败，尝试用其他管理员账号...')
    exit()

# 获取 courts 和 users
courts_resp = requests.get('http://127.0.0.1:5000/api/courts')
courts = courts_resp.json().get('data', [])

users_resp = requests.get('http://127.0.0.1:5000/api/users', headers={'Authorization': token})
users = users_resp.json().get('data', [])

print(f'场地数: {len(courts)}')
print(f'普通用户数: {len(users)}')

# 调用 optimize
opt_resp = requests.post('http://127.0.0.1:5000/api/optimize', 
    json={'courts': courts, 'users': users},
    headers={'Authorization': token}
)

import json
result = opt_resp.json()
print('\n=== /api/optimize 返回 ===')
print(json.dumps(result, indent=2, ensure_ascii=False))
