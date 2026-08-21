# 启动Flask并请求根路径查看调试信息
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
    r = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f'错误: {e}')
finally:
    proc.terminate()
    proc.wait()
