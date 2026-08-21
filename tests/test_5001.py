# 用5001端口启动Flask并测试
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
    # 请求根路径
    r = requests.get('http://127.0.0.1:5001/', timeout=5)
    print('根路径:', json.dumps(r.json(), indent=2, ensure_ascii=False))
    
    # 登录管理员
    r2 = requests.post('http://127.0.0.1:5001/api/login', 
        json={'username': 'admin', 'password': 'admin123'}, timeout=5)
    token = r2.json().get('data', {}).get('token', '')
    print('\n登录:', r2.json())
    
    if token:
        # 获取用户列表
        r3 = requests.get('http://127.0.0.1:5001/api/users', 
            headers={'Authorization': token}, timeout=5)
        print('\n用户列表:', json.dumps(r3.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
