import grpc
from concurrent import futures

from jnpy.app.grpc_service.proto import hello_pb2_grpc
from jnpy.app.grpc_service.proto import hello_pb2


class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return hello_pb2.HelloReply(message=f"你好hao， {request.name}")


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    server.wait_for_termination()