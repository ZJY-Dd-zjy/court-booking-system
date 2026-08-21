# 启动Flask并捕获输出
import subprocess
import time
import requests
import json
import threading

proc = subprocess.Popen(
    [r'C:\Users\five_\miniconda3\envs\flask-env\python.exe', r'C:\Users\five_\PycharmProjects\FlaskProject\app.py'],
    cwd=r'C:\Users\five_\PycharmProjects\FlaskProject',
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True
)

# 实时打印Flask输出
def read_output():
    for line in proc.stdout:
        print('[FLASK]', line.rstrip())

t = threading.Thread(target=read_output)
t.daemon = True
t.start()

time.sleep(4)

try:
    login_resp = requests.post('http://127.0.0.1:5000/api/login', json={'username': 'admin', 'password': 'admin123'}, timeout=5)
    token = login_resp.json().get('data', {}).get('token', '')
    
    users_resp = requests.get('http://127.0.0.1:5000/api/users', headers={'Authorization': token}, timeout=5)
    print('\n[API] /api/users 返回:')
    print(json.dumps(users_resp.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
