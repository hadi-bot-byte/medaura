import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc
import sys

class CalculatorSkeleton(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        result = request.num1 + request.num2
        return calculator_pb2.OperationResponse(result=result)
    def Sub(self, request, context):
        result = request.num1 - request.num2
        return calculator_pb2.OperationResponse(result=result)
    def Mul(self, request, context):
        result = request.num1 * request.num2
        return calculator_pb2.OperationResponse(result=result)
    def Div(self, request, context):
        result = request.num1 // request.num2
        return calculator_pb2.OperationResponse(result=result)
    def Mod(self, request, context):
        result = request.num1 % request.num2
        return calculator_pb2.OperationResponse(result=result)

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorSkeleton(), server)
    
    # Try different formats
    addresses = [
        'localhost:50051',
        '127.0.0.1:50051', 
        '0.0.0.0:50051',
        '[::]:50051',
        'localhost:8080',
        '127.0.0.1:8080'
    ]
    
    for address in addresses:
        try:
            server.add_insecure_port(address)
            print(f"✓ Successfully bound to {address}")
            server.start()
            print(f"Server running on {address}")
            server.wait_for_termination()
            return
        except Exception as e:
            print(f"✗ Failed to bind to {address}: {e}")
    
    print("All binding attempts failed!")

if __name__ == '__main__':
    run()