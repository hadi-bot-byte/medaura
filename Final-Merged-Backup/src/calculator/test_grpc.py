import grpc
print(f"gRPC version: {grpc.__version__}")

from concurrent import futures
import time

# Create server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

# Try multiple ports
ports_to_try = ['localhost:50051', '127.0.0.1:50052', 'localhost:50555', '127.0.0.1:60001']

for address in ports_to_try:
    try:
        server.add_insecure_port(address)
        print(f"✓ Successfully bound to {address}")
        server.start()
        print(f"Server started on {address}")
        time.sleep(2)  # Let server run for 2 seconds
        server.stop(0)
        print(f"Server stopped")
        break
    except Exception as e:
        print(f"✗ Failed to bind to {address}: {e}")