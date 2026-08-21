import subprocess, os, signal

# 查找占用5000端口的进程
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
pids = set()
for line in result.stdout.splitlines():
    if ':5000' in line and 'LISTENING' in line:
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():
                pids.add(pid)

print(f'发现占用5000端口的进程: {pids}')

for pid in pids:
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(f'已终止进程 PID={pid}')
    except Exception as e:
        print(f'终止 PID={pid} 失败: {e}')
