import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc
import time

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
    
    # Use this EXACT format - it works on Windows
    server.add_insecure_port('127.0.0.1:50051')
    
    server.start()
    print("✅ Server started on 127.0.0.1:50051")
    print("   (Press Ctrl+C to stop)")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    run()