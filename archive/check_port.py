import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', 5000))
print('5000端口被占用' if result == 0 else '5000端口空闲')
s.close()
