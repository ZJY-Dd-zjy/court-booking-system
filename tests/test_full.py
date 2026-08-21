# 启动Flask并测试optimize
import subprocess
import time
import requests
import json

# 启动Flask
proc = subprocess.Popen(
    [r'C:\Users\five_\miniconda3\envs\flask-env\python.exe', r'C:\Users\five_\PycharmProjects\FlaskProject\app.py'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

try:
    # 登录
    login_resp = requests.post('http://127.0.0.1:5000/api/login', json={'username': 'admin', 'password': 'admin123'}, timeout=5)
    print('登录:', login_resp.json())
    token = login_resp.json().get('data', {}).get('token', '')
    
    if token:
        courts_resp = requests.get('http://127.0.0.1:5000/api/courts', timeout=5)
        courts = courts_resp.json().get('data', [])
        
        users_resp = requests.get('http://127.0.0.1:5000/api/users', headers={'Authorization': token}, timeout=5)
        users = users_resp.json().get('data', [])
        
        print(f'场地: {len(courts)}, 用户: {len(users)}')
        
        opt_resp = requests.post('http://127.0.0.1:5000/api/optimize', 
            json={'courts': courts, 'users': users},
            headers={'Authorization': token}, timeout=10
        )
        print('\noptimize:')
        print(json.dumps(opt_resp.json(), indent=2, ensure_ascii=False))
    else:
        print('登录失败，尝试用 user/123456')
        login_resp2 = requests.post('http://127.0.0.1:5000/api/login', json={'username': 'user', 'password': '123456'}, timeout=5)
        print(login_resp2.json())

except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
