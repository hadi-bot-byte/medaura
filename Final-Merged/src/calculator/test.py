import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('127.0.0.1', 60001))
    print('Port 60001 is available')
    s.close()
except Exception as e:
    print(f'Error: {e}')