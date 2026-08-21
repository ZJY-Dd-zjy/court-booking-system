# 启动Flask并测试optimize（修正工作目录）
import subprocess
import time
import requests
import json

# 启动Flask（指定工作目录为项目根目录）
proc = subprocess.Popen(
    [r'C:\Users\five_\miniconda3\envs\flask-env\python.exe', r'C:\Users\five_\PycharmProjects\FlaskProject\app.py'],
    cwd=r'C:\Users\five_\PycharmProjects\FlaskProject',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

try:
    login_resp = requests.post('http://127.0.0.1:5000/api/login', json={'username': 'admin', 'password': 'admin123'}, timeout=5)
    token = login_resp.json().get('data', {}).get('token', '')
    print('登录:', login_resp.json())
    
    if token:
        users_resp = requests.get('http://127.0.0.1:5000/api/users', headers={'Authorization': token}, timeout=5)
        print('\n/api/users 原始返回:')
        print(json.dumps(users_resp.json(), indent=2, ensure_ascii=False))
        
        courts_resp = requests.get('http://127.0.0.1:5000/api/courts', timeout=5)
        courts = courts_resp.json().get('data', [])
        users = users_resp.json().get('data', [])
        
        print(f'\n场地: {len(courts)}, 用户: {len(users)}')
        
        opt_resp = requests.post('http://127.0.0.1:5000/api/optimize', 
            json={'courts': courts, 'users': users},
            headers={'Authorization': token}, timeout=10
        )
        print('\noptimize:')
        print(json.dumps(opt_resp.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
