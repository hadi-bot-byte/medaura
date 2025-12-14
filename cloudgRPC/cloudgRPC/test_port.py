import socket

def test_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        print(f"Port {port} is available")
        sock.close()
        return True
    except OSError as e:
        print(f"Port {port} is NOT available: {e}")
        return False

# Test some ports
test_port(50051)
test_port(50052)
test_port(50555)
test_port(8080)
test_port(9000)